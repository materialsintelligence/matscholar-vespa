import os
import pymongo
import json
from tqdm import tqdm
from datetime import datetime, timedelta

client = pymongo.MongoClient(os.getenv("MATSCHOLAR_PROD_HOST"),
                             username=os.getenv("MATSCHOLAR_PROD_USER"),
                             password=os.getenv("MATSCHOLAR_PROD_PASS"),
                             authSource=os.getenv("MATSCHOLAR_PROD_DB"))

db = client[os.getenv("MATSCHOLAR_PROD_DB")]

# if sys.argv and sys.argv[1] == "1":
#     entries = db.entries_vespa_upload.find({})
# elif sys.argv and sys.argv[1] == "2":
#     entries = db.entries_vespa_upload.find({"fields.timestamp":{"$gt":(datetime.now() - timedelta(7)).timestamp()}})
# else:
#     entries = db.entries_vespa_upload.find({"synced": False})

key_dict = {"MAT": "materials",
            "SPL": "phase_labels",
            "CMT": "characterization_methods",
            "PRO": "properties",
            "SMT": "synthesis_methods",
            "APL": "applications",
            "DSC": "descriptors",
            "MAT_clean": "materials_clean"
            }

if not os.path.exists('feed_files'):
    os.makedirs('feed_files')

for year in range(2019, 1900, -1):
    print("Building feed file for ", year, "...")
    entries = db.entries_entities.find({'year': year})
    if entries.count():
        with open(f"feed_files/feed-file-temp-{year}.json", "w") as file:
            ids = []
            for entry in tqdm(entries, total=entries.count()):
                if not "year" in entry:
                    # 5 documents in db don't have a year. Manually checked and they all are from 2016
                    entry["year"] = "2016"

                delkeys = []

                if isinstance(entry["authors"], str):
                    entry["authors"] = [entry["authors"]]

                id = str(entry["_id"])
                ids.append(entry["_id"])
                delkeys.append("_id")

                if "issn" in entry:
                    delkeys.append("issn")


                for key in list(entry.keys()):
                    if "summary" in key:
                        delkeys.append(key)
                    if key in key_dict:
                        entry[key_dict[key]] = entry[key]
                        delkeys.append(key)

                entry["timestamp"] = int(datetime(int(entry["year"]), 1, 1).timestamp())

                entry["year"] = str(entry["year"])

                entry["journal"] = db.entries.find_one({"doi": entry["doi"]}).get("journal", "")
                if isinstance(entry["journal"], list):
                    entry["journal"] = entry["journal"][0]
                elif not len(entry["journal"]):
                    # TODO: write script to repair journals
                    entry["journal"] = "Unknown"

                for key in delkeys:
                    del entry[key]

                entry = {"put": f"id:matscholar:doc::{id}", "fields": entry}
                file.write(json.dumps(entry))
                file.write("\n")
    print("Done")

# db.entries_vespa_upload.update_many({"_id": {"$in": ids}}, {"$set": {"synced":True}})