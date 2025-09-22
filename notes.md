## potential rules for parsing
- each line can be one of three things
1. begins with "#", signifying that the whole line is a comment
2. begins wtih "[", signifying a title or header representing a segment of information
3. begins with any other character, assumed to be a line of data to be processed
- each line of data is expected to take the following format
1. a string of text, representing the name for this data
2. the "=" character
3. another string for the value being stored


## input assumptions
- input is always a .ini file
- every line of data needs to be represented visually in the final product
- data under each [header] should be grouped together
- custpartno == S/N


## plan
- write code to process the .ini to .xml format
- dont worry about making it correct. just output something and then bruce can tell me what is wrong with it
- 

## questions
- do you have any old report/input file pairs?
- discuss visual details of the ini input
