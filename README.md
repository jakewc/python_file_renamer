Python Basic Challenge

 

Below is a simple code challenge. What we'd like to see is how you solve problems and deliver solutions in the real world. What do you believe is important to include for a production solution? Give us a sense of your skill, style and polish!

 

It's okay if you make assumptions, but tell us what your assumptions are and why they make sense.

 

Please write a tool to assist with renumbering sequences of images:

 

•             The tool should take path to a directory, for example:

<program> [options] </path/to/directory/of/images> [...]

•             The directory should contain a bunch of images files

•             An image sequence should follow the pattern: <name>.<number>.<extension>

•             All images in a sequence must share the same <name> and <extension>

 

For example:

 

•             prodeng.01.jpg and prodeng.27.jpg are part of the same sequence

•             prodeng.01.jpg and prodeng.27.png are NOT part of the same sequence

•             prodeng.01.jpg and weta.02.jpg are NOT part of the same sequence

 

You can assume the following:

 

•             The numbers are always zero padded

•             All sequences start at 01

•             Extra credit if you can make it work without these assumptions!

 

Your tool should rename the files in the directory so that each sequence remains in the same order, but the files are renumbered sequentially.

 

For example for a directory containing these files:

 

=prodeng.11.jpg prodeng.11.png prodeng.27.jpg prodeng.32.jpg prodeng.32.png prodeng.33.png prodeng.47.png prodeng.55.jpg prodeng.55.png prodeng.56.jpg prodeng.68.jpg prodeng.72.png prodeng.94.png weta.17.jpg weta.22.jpg weta.37.jpg weta.55.jpg weta.96.jpg=

 

The output should be:

 

=prodeng.01.jpg prodeng.02.jpg prodeng.03.jpg prodeng.04.jpg prodeng.05.jpg prodeng.06.jpg prodeng.01.png prodeng.02.png prodeng.03.png prodeng.04.png prodeng.05.png prodeng.06.png prodeng.07.png weta.01.jpg weta.02.jpg weta.03.jpg weta.04.jpg weta.05.jpg=
