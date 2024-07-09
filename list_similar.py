"""Healthtec page of teknologiateollisuus is not optimal for
searching companies based on their activities and locations

One can use this python script to list and search for assets
produced by the scraping script. Some examples are given.
"""

__date__ = "2024-07-09"
__author__ = "github.com/vahvero"

# %%

import json

# %%

with open("company_kw.json") as fobj:
    data = json.load(fobj)

keywords = set(x for keys in data.values() for x in keys)

print(f"Keywords (n={len(keywords)}):", "\n\t" + "\n\t".join(keywords))


# %%
def find_companies(*keys):
    assert all(
        key in keywords for key in keys
    ), "Some key does not exist in the keywords set"
    companies = list(
        x[0] for x in filter(lambda x: all(key in x[1] for key in keys), data.items())
    )
    print(
        f"Companies with keywords: {', '.join(keys)} (n={len(companies)})",
        "\n\t" + "\n\t".join(companies),
    )


def list_characteristics(*names):
    for key, elems in data.items():
        for name in names:
            if name in key:
                out = f"{key}:\n\t" + "\n\t".join(elems)
                print(out)
                break


# %%
list_characteristics("aiforia", "revenio")

# %%
list_characteristics("taika3d")

# %%

find_companies("ohjelmisto", "Helsinki")

# %%

find_companies("ohjelmisto", "Espoo")

# %%

find_companies("kuvantaminen", "Helsinki")
# %%

find_companies("kuvantaminen", "Espoo")

# %%

find_companies("Espoo")

# %%

find_companies("tekoäly", "Espoo")
# %%

find_companies("tekoäly", "Helsinki")

# %%
