JsRefactoring
=============

A simple set of tools to aid in refactoring.  This is meant to augment JsFormat.

Current Commands
----------------

```
js_hoist_vars
```

Consolidate all var definitions of the current function into the first var statment.


Install
-------
You may install `JsRefactoring` using git with the below commands:

*Linux*

    `git clone git://github.com/aearly/JsRefactoring.git ~/.config/sublime-text-2/Packages/JsRefactoring`

*MacOSX*

    `git clone git://github.com/aearly/JsRefactoring.git ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/JsRefactoring`

*Windows*

    `git clone git://github.com/aearly/JsRefactoring.git "%APPDATA%\Sublime Text 2\Packages\JsRefactoring"`

TODO
-------

- Use/write an AST generator
- JS Hoist
	- Respect indentation
	- Remove secondary delcarations with no assignment
	- Key binding
- Add feature to auto-wrap `for each` blocks in hasOwnProperty()
- Add feature to auto convert `for` loops to `_.each`
- Add feature to find global leaks
