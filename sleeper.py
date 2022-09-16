import time
import requests
import client
import json
import csv

our_client = client.Client()

def snooze(snoozy=True):
  if snoozy:
    return time.sleep(60)

def list_walks(foo=42):
  walks = json.loads(our_client.get("http://sillywalks.gov.uk/walks"))
  return [walk for walk in walks if walk['silliness'] > 5]

def do_complicated_thing():
   return our_client.do(the='thing').zhu('li')

def fundamentally_broken():
  raise RuntimeError("Out Of Cheese Error")

def csv_reader():
  return csv.reader()
