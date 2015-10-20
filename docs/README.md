Quickstart
==========

You will need sphinx to build the documentation. You can install it via pip:

    pip install sphinx

The documentation looks better with the following package installed,
however it is not requried:

    pip install sphinx-better-theme

Once you have sphinx installed, you can build the documentation by
running the following command from this directory:

    sphinx-build source html

The second argument of the above command is the output directory. In
other words this will generate the documentation into the "html"
directory. If you wish to put it somewhere else you may supply a
different path. Once the build completes you can point your web
browser at the output directory you supplied and inspect the result.

Details
=======

Documentation is written using Sphinx.  You must have [Sphinx
installed](http://sphinx-doc.org/latest/install.html) to build the
documentation.

Example Tags
============

You can put python files in source/examples which can be
referenced as examples from within the documentation/tutorials.

To make a named tag within an example python file, use a line of the
form `# <tag_name>` to begin the tag (`qwhere `tag_name` is replaced
with the name of the tag) and a line of the form `# </tag_name>` to
end the tag.  Tags *do not* have to be properly nested.

Upon build, tags will be preprocessed into new source files in the
source/tags directory.  If the example file was called
source/examples/example1.py and contained the tags `hello`, `world`,
and `python`, the files in the tags directory after preprocessing
would be source/tags/example1.py, source/tags/example1.py.hello.py,
source/tags/example1.py.world.py, and
source/tags/example1.py.python.py

**NOTE**: *Files in source/tags are automatically generated and should
  never be editted directly*.

To show the source of one of the tags files in a documentation file (.rst), use the syntax:

```
.. literalinclude:: ../tags/example1.py.hello.py
```

(with the path replaced appropriately).

Example:

source/examples/test.py:

```python
# hello
# <tag3>
# <tag1>
# A comment
print "Hello world!"
# </tag1>
# <tag2>
# Another comment
print "hello world2!"
# </tag3>
# </tag2>
```
