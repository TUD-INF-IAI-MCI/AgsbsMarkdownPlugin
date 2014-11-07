Agsbs Markdown Helper
===================

**This plugin is in a developing state, not stable**

This is a sublime plugin which is used in our working group. Our working group is transcribing study materials
for blind and visual impaired students ([Elvis - german Website](http://elvis.inf.tu-dresden.de)).

After the creation of the Markdown files a customized pandoc converter is used for the transformation to HTML 
([pandoc-website](http://johnmacfarlane.net/pandoc/))

## The Plugin
The plugin offered different functions to fulfil our guidelines, add Markdown content and 
helps unknown transcribers to create markdown-files.

Also a validation is possible.


### Shortcut

There are shortcuts for the generation of content like folder structure, convert to HTML or check the md-content by our check-tool. All these commands are set to the function-keys (see table below)

#### Shortcuts for Generation/Conversion of content

| Shortcut | Explanation                                |
| -----    | -------                                    |
| F2       | create structure                           |
| F3       | check the selected Markdown-file           |
| F4       | create toc-file (index.md)                 |
| F5       | convert the selected Markdown-file to HTML |
| F6       | not support yes                            |
| F7       | show the selected HTML in browser          |

#### Shortcuts for the transcription

The following shortcuts helps during the transcriptions 

| Shortcut   | Selection required | Explanation                                                               |
| ---------- | --------------     | ------------------------------------------------------------------------- |
| ALT+SHIFT+h      | yes                | insert heading markdown for level 1, multiple input is supported          |
| ALT+SHIFT+r      | no                 | horizontal row                                                            |
| ALT+SHIFT+i      | yes                | markdown syntax for italic                                                |
| ALT+SHIFT+s      | yes                | markdown syntax for strong/bold                                           |
| ALT+SHIFT+o      | yes                | ordered list                                                              |
| ALT+SHIFT+u      | yes                | unordered list                                                            |
| ALT+SHIFT+q      | yes                | quotes                                                                    |
| ALT+SHIFT+t      | no                 | table syntax                                                              |
| ALT+SHIFT+c      | yes                | insert tabs for code format                                               |
| ALT+SHIFT+l      | no                 | markdown syntax for a link, input the link text and URL via inputs fields |
| ALT+SHIFT+p      | no                 | add syntax for page, input page number below                              |
| CTRL+ALT+i | no                 | markdown syntax for image and alternative description, input via text fields                     |


