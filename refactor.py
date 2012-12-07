import sublime
import sublime_plugin
import re


def subtract_region(lhs, rhs):
    start = lhs.a
    end = lhs.b

    if rhs.a < lhs.a:
        if rhs.b > lhs.a:
            start = rhs.b
            if rhs.b >= lhs.b:
                return []  # lhs is contained within rhs
        else:
            return [lhs]  # rhs is entirely before lhs
    else:
        if rhs.a < lhs.b:
            end = rhs.a
            if rhs.b < lhs.b:
                # split into 2 regions
                return [sublime.Region(start, end), sublime.Region(rhs.b, lhs.b)]
        else:
            return [lhs]  # rhs is entirely after lhs, return

    return [sublime.Region(start, end)]


def subtract_from_regions(regions, rhs):
    new = []
    for reg in regions:
        new += subtract_region(reg, rhs)
    return new


def block_contains(block, reg):
    return any(x.contains(reg) for x in block)


def get_current_body(view, cursor):
    blocks = []
    # find all function keywords
    for function in view.find_all("function"):
        # skip comments
        if "function" not in view.scope_name(function.b - 1):
            continue

        depth = 1
        not_comment = 1
        # find the opening brace
        fun_start = brace = view.find("\\{", function.b)
        while depth > 0:
            brace = view.find(r"\{|\}|\/\*|\*\/|\/\/.+$", brace.b)
            try:
                string = view.substr(brace)
                if string == "/*":
                    not_comment = 0
                elif string == "*/":
                    not_comment = 1
                elif string == "{":
                    depth += 1 * not_comment
                elif string == "}":
                    depth -= 1 * not_comment
            except:
                raise Exception("error around %d, %d" % (view.rowcol(function.b)))

        blocks.append(sublime.Region(fun_start.b, brace.a))

    # make every element a list
    blocks = [[block] for block in blocks]

    # cut out blocks from containting closure functions
    for i in range(len(blocks)):
        for j in range(i):
            blocks[j] = subtract_from_regions(blocks[j], blocks[i][0])

    #flatten array
    #flatblocks = [block for list in blocks for block in list]
    #view.add_regions("hoister_functions", flatblocks, "code", "", sublime.DRAW_OUTLINED)

    for block in blocks:
        for region in block:
            if region.contains(cursor):
                return block
    return []


def find_vars(view, block):
    # grab the text of every region, and concatenate, strip out line breaks
    text = "__BLOCK__".join([view.substr(region) for region in block])
    vars = []
    for statement in re.findall("var([^;]+);", text):
        strstatement = "".join(re.split(r"\{[^\}]+\}|\[[^\]]+\]|\([^\)]+\)", statement))
        # split on commas, then split on "=", strip whitespace from result
        vars.append([arg.split("=")[0].strip() for arg in strstatement.split(",")])
    return vars


def find_var_blocks(view, block):
    start = block[0].a
    end = block[-1].b
    vars = []

    while start < end:
        varbegin = view.find("[^\w](var) ", start)
        if not varbegin or varbegin.a > end:
            break

        varbegin = view.find("var", varbegin.a)

        if not block_contains(block, varbegin):
            start = varbegin.b
            continue

        varend = varbegin
        while True:
            varend = view.find(";", varend.b)
            if block_contains(block, varend):
                break

        vars.append(sublime.Region(varbegin.a, varend.b))
        start = varend.b

    return vars


def find_var_names(view, blocks):
    vars = []
    for block in blocks:
        ident = view.find("[a-zA-Z_$][0-9a-zA-Z_$]*", block.a + 4)
        vars.append(ident)
        tok = ident
        level = 0
        not_comment = 1
        while tok.a < block.b:
            tok = view.find(r"[,\{\}\[\]\(\);]|\/\*|\*\/|\/\/.*$", tok.b)
            string = view.substr(tok)
            if string == ";" and level == 0:
                break
            elif string in ["{", "[", "("]:
                level += 1 * not_comment
            elif string in ["}", "]", ")"]:
                level -= 1 * not_comment
            elif string == "/*":
                not_comment = 0
            elif string == "*/":
                not_comment = 1
            elif string == "," and level == 0:
                tok = view.find("[a-zA-Z_$][0-9a-zA-Z_$]*", tok.b)
                vars.append(tok)

    return vars


class JsHoistVarsCommand(sublime_plugin.TextCommand):
    """
    Consolidate all var statements to the top of the current function
    """
    def run(self, edit):
        view = self.view
        view.erase_regions("hoister_function")
        if "JavaScript" not in view.settings().get('syntax'):
            return
        cursor = view.sel()[0]

        block = get_current_body(view, cursor)

        #print find_vars(view, block)
        var_statements = find_var_blocks(view, block)
        vars = find_var_names(view, var_statements)
        #print vars
        #view.add_regions("hoister_function", var_statements, "code", "", sublime.DRAW_OUTLINED)

        if len(var_statements) == 0:
            return

        to_add = []

        for statement in var_statements[1:]:
            for var in vars:
                if statement.contains(var):
                    to_add.append(view.substr(var))

        for statement in reversed(var_statements[1:]):
            view.erase(edit, sublime.Region(statement.a, statement.a + 4))

        varbegin = var_statements[0].a
        indent_char = view.substr(sublime.Region(varbegin - 1, varbegin))
        indent = view.rowcol(varbegin)[1]
        indent = indent + 1 if indent_char == "\t" else indent + 2
        sep = ",\n" + indent_char * indent
        view.insert(edit, var_statements[0].b - 1, sep + sep.join(to_add))

