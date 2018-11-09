import localstack_client.session
import boto3
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import sys
import datetime
import time

STREAM = 'sfr-epub-ingest-development'

#SESSION = localstack_client.session.Session()
#KINESIS = SESSION.client('kinesis')
KINESIS = boto3.client('kinesis', region_name='us-east-1')
SHARD = KINESIS.list_shards(StreamName=STREAM)["Shards"][0]
SHARDID = SHARD["ShardId"]
STARTINGSEQ = SHARD["SequenceNumberRange"]["StartingSequenceNumber"]

CONN = psycopg2.connect("dbname=sfr_test user=sfr_tester password=guten")

GET_ITEMS = "SELECT id, url, size, date_modified FROM items WHERE id > 60"

def putRecords():

    cursor = CONN.cursor(cursor_factory=RealDictCursor)

    cursor.execute(GET_ITEMS)

    items = cursor.fetchall()

    counter = 0
    for item in items:
        itemBytes = json.dumps({
            "id": item["id"],
            "url": item["url"],
            "size": item["size"],
            "updated": item["date_modified"].strftime('%Y-%m-%d')
        }).encode("utf-8")

        resp = KINESIS.put_record(
            StreamName=STREAM,
            Data=itemBytes,
            PartitionKey=SHARDID
        )
        print("PUT {}".format(item["id"]))
        counter += 1
        if counter >= 5:
            break


def getRecords():
    resp = KINESIS.get_shard_iterator(
        StreamName=STREAM,
        ShardId=SHARDID,
        ShardIteratorType="AT",
    )
    iterator = resp["ShardIterator"]
    print(iterator)
    while True:

        recResp = KINESIS.get_records(
            ShardIterator=iterator,
            Limit=25
        )
        recs = recResp["Records"]
        iterator = recResp["NextShardIterator"]
        for rec in recs:
            recData = json.loads(rec["Data"])
            print(recData)
        if recResp["MillisBehindLatest"] == 0:
            break
        print("Trying...", recResp["MillisBehindLatest"])
        time.sleep(0.2)


if __name__ == '__main__':
    args = sys.argv
    if args[1] == "GET":
        getRecords()
    elif args[1] == "PUT":
        putRecords()
