import boto3
import json
import sys
import datetime
import time

# Streams
# sfr-epub-results-development
# sfr-gutenberg-metadata-development

KINESIS = boto3.client('kinesis', region_name='us-east-1')

def getRecords(fromTime=None, stream=None):

    shard = KINESIS.list_shards(StreamName=stream)["Shards"][0]
    shardID = shard["ShardId"]
    startingSeq = shard["SequenceNumberRange"]["StartingSequenceNumber"]

    # If we don't set a time, get records updated in the past hour
    if fromTime is None:
        now = datetime.datetime.utcnow()
        fromTime = now + datetime.timedelta(hours = -1)
    print(fromTime)
    resp = KINESIS.get_shard_iterator(
        StreamName=stream,
        ShardId=shardID,
        ShardIteratorType="AT_TIMESTAMP",
        Timestamp=fromTime
    )
    iterator = resp["ShardIterator"]
    while True:

        recResp = KINESIS.get_records(
            ShardIterator=iterator,
            Limit=25
        )
        recs = recResp["Records"]
        iterator = recResp["NextShardIterator"]
        for rec in recs:
            recData = json.loads(rec["Data"])
            if stream == 'sfr-epub-results-development':
                if "data" not in recData:
                    continue
                if "type" not in recData["data"]:
                    continue
                print("==========={}===========".format(recData["data"]["id"]))
                print("Status: {}| {}".format(recData["status"], recData["message"]))
                print("{} ({})".format(recData["data"]["url"], recData["data"]["type"]))
                print("Updated: {}".format(str(recData["data"]["date_updated"])))
                if recData["data"]["type"] == 'archive':
                    print("md5 Hash: {}".format(recData["data"]["etag"]))
                print("===========END===========")
            else:
                print(recData)
        if recResp["MillisBehindLatest"] == 0:
            break
        time.sleep(0.2)

if __name__ == '__main__':
    args = sys.argv
    fromTime = None
    if len(args) > 2:
        if args[1] != 'None':
            fromTime = datetime.datetime.strptime(args[1], "%Y-%m-%dT%H:%M:%S.%fZ")
        stream=args[2]
    getRecords(fromTime=fromTime, stream=stream)
