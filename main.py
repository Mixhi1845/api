from fasthtml.common import *
import requests
from bs4 import BeautifulSoup

app, rt = fast_app()


@app.get("/")
def home():
    return Socials(
        title="Vitrina API",
        site_name="Vitrina",
        description="The API for the chart agregator Vitrina",
        image="https://vercel.fyi/fasthtml-og",
        url="https://api.vitrina.michaelwagner.cc",
    ), Ul(
        Li(A("billboard-global-200", href="/api/v1/billboard-global-200")),
        Li(A("imdb", href="/api/v1/imdb")),
        Li("limc", href="/api/v1/limc"),
        Li(A("netflix-top-10", href="/api/v1/netflix-top-10")),
        Li(A("nyt-bestsellers", href="/api/v1/nyt-bestsellers")),
    )


@rt("/api/v1/billboard-global-200")
def get():
    urls = {
        "music": "https://www.billboard.com/charts/billboard-global-200/",
    }

    results = {}

    for key, url in urls.items():
        page = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(page.content, "html.parser")

        top_items = []

        for i in range(2, 250):
            list_item = soup.select_one(
                f"div.o-chart-results-list-row-container:nth-of-type({i})"
            )
            if list_item:

                col1_item = list_item.select_one(
                    f"li.o-chart-results-list__item:nth-of-type({1})"
                )
                if col1_item:
                    id = int(col1_item.select_one("span.c-label").text.strip())

                # TODO: Album hrefs

                col3_item = list_item.select_one(
                    f"li.o-chart-results-list__item:nth-of-type({3})"
                )
                if col3_item:
                    type = col3_item.select_one("span.c-label")
                    if type:
                        type = type.text.strip().replace("\n", "")
                    else:
                        type = None

                col4_item = list_item.select_one(f"li.lrv-u-width-100p")
                if col4_item:
                    title = col4_item.select_one("h3.c-title").text.strip()
                    artist = col4_item.select_one("span.c-label").text.strip()
                    col4_1_item = list_item.select_one(
                        f"li.o-chart-results-list__item:nth-of-type({5})"
                    )
                    if col4_1_item:
                        peak = int(col4_1_item.select_one("span.c-label").text.strip())
                    col4_2_item = list_item.select_one(
                        f"li.o-chart-results-list__item:nth-of-type({6})"
                    )
                    if col4_2_item:
                        wks = int(col4_2_item.select_one("span.c-label").text.strip())

            info = {
                "id": id,
                "title": title,
                "artist": artist,
                "type": type,
                "peak": peak,
                "wks": wks,
            }
            if info not in top_items:
                top_items.append(info)

        data = soup.select_one("div.pmc-paywall")
        if data:
            data_title = soup.select_one("h1.c-heading")
            data_desc = soup.select("p.c-tagline")[0]
            data_date = soup.select("p.c-tagline")[6]

        nested_data = {
            "data_title": data_title.text.strip(),
            "data_desc": data_desc.text.strip(),
            "data_date": data_date.text.strip(),
            "data": top_items,
        }

        results[key] = nested_data

    return results


@rt("/api/v1/imdb")
def get():
    urls = {
        "movies": "https://www.imdb.com/chart/moviemeter/",
        "tv_shows": "https://www.imdb.com/chart/tvmeter/",
    }

    results = {}

    for key, url in urls.items():
        page = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(page.content, "html.parser")

        top_items = []

        for i in range(1, 101):
            list_item = soup.select_one(
                f"li.ipc-metadata-list-summary-item:nth-of-type({i})"
            )
            if list_item:
                title = list_item.select_one("h3.ipc-title__text").text
                rank_text = list_item.select_one("div.meter-const-ranking").text
                rank = int(rank_text.split(" ")[0])

                year_element = list_item.select_one(
                    f"span.cli-title-metadata-item:nth-of-type(1)"
                )
                if year_element:
                    year = year_element.text.replace("\u2013", "-")
                else:
                    year = "N/A"

                length_element = list_item.select_one(
                    f"span.cli-title-metadata-item:nth-of-type(2)"
                )
                if length_element:
                    length = length_element.text
                else:
                    length = "N/A"

                age_element = list_item.select_one(
                    f"span.cli-title-metadata-item:nth-of-type(3)"
                )
                if age_element:
                    age = age_element.text
                else:
                    age = "N/A"

                rating_text = list_item.select_one("span.ipc-rating-star").text
                if "\xa0" in rating_text:
                    rating, num_votes = rating_text.split("\xa0")
                    num_votes = num_votes.strip("()")
                else:
                    rating = rating_text
                    num_votes = "N/A"

                anchor = list_item.select_one("a.ipc-title-link-wrapper")
                if anchor:
                    href = anchor.get("href")

                info = {
                    "title": title.strip(),
                    "rank": rank,
                    "year": year,
                    "length": length.strip(),
                    "age": age.strip(),
                    "href": href,
                    "rating": rating,
                    "num_votes": num_votes,
                }
                top_items.append(info)

        data_title = soup.select_one("h1.ipc-title__text")
        data_desc = soup.select_one("div.ipc-title__description")

        nested_data = {
            "data_title": data_title.text.strip() if data_title else "N/A",
            "data_desc": data_desc.text.strip() if data_desc else "N/A",
            "data": top_items,
        }

        results[key] = nested_data

    return results


@rt("/api/v1/limc")
def get():
    return P("coming soon")


@rt("/api/v1/netflix-top-10")
def get():
    urls = {
        "movies": "https://www.netflix.com/tudum/top10",
        "tv_shows": "https://www.netflix.com/tudum/top10/tv",
    }

    results = {}

    for key, url in urls.items():
        page = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(page.content, "html.parser")

        top_items = []

        table = soup.select_one("table")
        rows = table.select("tr")[1:]  # Skip the first row

        for row in rows:
            rank_element = row.select_one("td:nth-of-type(1)")
            if rank_element:
                rank = int(rank_element.text)
            else:
                rank = "N/A"

            title_element = row.select_one("td:nth-of-type(2)")
            if title_element:
                title_text = title_element.text.strip()
                if ":" in title_text:
                    title, episode = title_text.split(":", 1)
                    title = title.strip()
                    episode = episode.strip()
                else:
                    title = title_text
                    episode = None
            else:
                title = "N/A"
                episode = None

            wks_element = row.select_one("td:nth-of-type(3)")
            if wks_element:
                wks = int(wks_element.text)
            else:
                wks = "N/A"

            views_element = row.select_one("td:nth-of-type(6)")
            if views_element:
                views = int(views_element.text.replace(",", ""))
            else:
                views = "N/A"

            info = {
                "rows": rank,
                "title": title,
                "episode": episode,
                "wks": wks,
                "views": views,
            }
            top_items.append(info)

        data_title = soup.select("span.pagetext")[5]
        data_desc = soup.select("span.pagetext")[6]
        data_updated = soup.select("div.uppercase")[10]

        nested_data = {
            "data_title": data_title.text.strip(),
            "data_desc": data_desc.text.strip(),
            "data_updated": data_updated.text.strip(),
            "data": top_items,
        }

        results[key] = nested_data

    return results


@rt("/api/v1/nyt-bestsellers")
def get():
    urls = {
        "books": "https://www.nytimes.com/books/best-sellers/",
    }

    results = {}

    for key, url in urls.items():
        page = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(page.content, "html.parser")

        top_items = []

        chart_item = soup.select_one(f"div.css-v2kl5d:nth-of-type(2)")
        for j in range(1, 6):
            list_item = chart_item.select_one(f"li.css-19afmtv:nth-of-type({j})")
            if list_item:
                title = list_item.select_one("h3.css-i1z3c1")
                author = list_item.select_one("p.css-1nxjbfc")
                wks = list_item.select_one("p.css-t7cods")
                desc = list_item.select_one("p.css-5yxv3r")

            info = {
                "title": title.text.strip(),
                "author": author.text.strip(),
                "wks": wks.text.strip(),
                "desc": desc.text.strip(),
            }
            top_items.append(info)

        data_desc = soup.select_one("h2.css-2j7wu4")
        data_updated = soup.select_one("time.css-6068ga")

        nested_data = {
            "data_desc": data_desc.text.strip(),
            "data_updated": data_updated.text.strip(),
            "data": top_items,
        }

        results[key] = nested_data

    return results


serve()
