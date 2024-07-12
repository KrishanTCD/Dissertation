# you will need to run turbostat on your machine 
For windows the command will be :

Get-Counter '\Processor(_Total)\% Processor Time' -Continuous -SampleInterval 1 | Export-Csv -Path C:\path\to\output.'file_format'

#Post getting the file
1. Store Automation file, pdf file, docker file within same file folder as well as requirements.txt

# Run the first command mentioned in docker file  in terminal to build the docker image

# Run the second command mentioned in docker file in terminal to run the docker image inlcuding the path to your output.csv

# the program is capable of handling multiple csv file
