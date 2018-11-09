# ResearchNow Utilities
These scripts contain several tools that can be used to invoke test instances of the ResearchNow data ingest pipeline. They can also be used to read results from the Kinesis streams that make up this pipeline. At present there are two scripts that provide this monitoring, but it is likely that others will be added.

## Installation
This repo can be cloned and the dependencies installed from the requirements.txt via pip. The scripts are compatible with python3 (up through 3.7) only

## Scripts
### ePub Kinesis Ingest
This script can read or write to the Kinesis stream that triggers the lambda that processes and stores the ePubs in s3. At present the ingest process runs off of a locally stored postgresql instance, so that mode will fail. However it can be used to monitor the status of the ingest stream.It can be run with `python3 psqlToKinesis.py GET` This will trigger an export of all records put to the Kinesis stream in the past 24 hours. Please be aware that due to throttling limits imposed by Kinesis, this can take some time to catch up to the present and produce results

### ePub Ingest Result
This script reports on the most recently stored results in s3 (up to the past 24 hours). By default it will generate a list of files stored in the past hour but this can be adjust by passing a timestamp to the script. It is invoked with `python3 getIngestresults.py [optional-timestamp]` The report includes the zipped files and the links to the content.opf file of each exploded ePub file. These links can then be verified for access/fidelty/accuracy. The timestamp should be formatted as **2018-11-09T12:00:00Z**
