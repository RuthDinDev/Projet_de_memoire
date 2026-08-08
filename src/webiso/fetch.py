"""Validation d'URL et chargement HTTP de pages HTML."""

import socket

import requests
from urllib.parse import urlparse


def valider_url(url):
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    if not urlparse(url).netloc:
        raise ValueError(f"URL invalide : '{url}'")
    return url


def charger_page(url, timeout=10):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; StructureExtractor/1.0)"}
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        return r.text
    except requests.exceptions.ConnectionError:
        raise ConnectionError(f"Connexion impossible : '{url}'")
    except requests.exceptions.Timeout:
        raise TimeoutError(f"Délai dépassé : '{url}'")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Erreur HTTP : {e}")
    except socket.gaierror:
        raise ConnectionError(f"Hôte introuvable : '{url}'")
