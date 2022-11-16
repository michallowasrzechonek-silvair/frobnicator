import logging
import requests


def frobnicate(partner_name):
    log = logging.getLogger(f"frobnicate.{partner_name}")

    partner_url = f"https://api.platform-prod.silvair.com/partners/{partner_name}"

    log.info("Fetch %s", partner_url)
    partner_response = requests.get(partner_url)
    partner_object = partner_response.json()

    documents = {}
    for document_object in partner_object.get("latestDocuments", [])[:1]:
        document_title = document_object["label"]
        document_url = document_object["url"]
        log.info("Fetch %s from %s", document_title, document_url)

        document_response = requests.get(document_url, stream=True)
        documents[document_title] = document_response.raw.read()

    log.info("%s", partner_object)
    log.info("%s", {title: len(content) for title, content in documents.items()})
    return partner_object, documents
