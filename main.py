from fasthtml.common import *
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

app = FastHTML()


@app.get("/")
def home():
    return (
        Title("Vitrina API"),
        Socials(
            title="API Index",
            site_name="Vitrina API",
            description="The API for the chart agregator Vitrina",
            image="https://vercel.fyi/fasthtml-og",
            url="https://api.vitrina.michaelwagner.cc",
        ),
        Ul(
            Li(A("✅ pw-top-10", href="/api/v1/pw-top-10")),
            Li(A("✅ appstore-iphone", href="/api/v1/appstore-iphone")),
            Li(A("✅ billboard-global-200", href="/api/v1/billboard-global-200")),
            Li(A("✅ imdb", href="/api/v1/imdb")),
            Li(A("✅ netflix-top-10", href="/api/v1/netflix-top-10")),
            Li(A("✅ steam-most-popular", href="/api/v1/steam-most-popular")),
        ),
    )


@app.get("/api/v1/pw-top-10")
def pw():
    urls = {
        "books": "https://www.publishersweekly.com/pw/nielsen/top100.html",
    }

    results = {}

    for key, url in urls.items():
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        top_items = []
        table = soup.select_one("table")
        rows = table.select("tr")[1:]  # Skip the first row

        for row in rows[:25]:
            cells = row.find_all("td")

            rank = cells[0].text.strip() if cells[0] else "N/A"
            wks = cells[2].text.strip() if cells[2] else "N/A"
            title = (
                cells[3].select_one("div.nielsen-booktitle").text.strip()
                if cells[3]
                else "N/A"
            )
            author = (
                cells[3].select_one("div:nth-of-type(2)").text.strip(", Author")
                if cells[3]
                else "N/A"
            )
            author = author.title()  # Convert to title case
            pub = cells[4].text.strip() if cells[4] else "N/A"

            info = {
                "rank": rank,
                "wks": wks,
                "title": title,
                "author": author,
                "pub": pub,
            }
            top_items.append(info)

        data_title = soup.select_one("div.nielsen-header").text.strip()
        data_info = {
            "data_title": data_title,
            "data": top_items,
        }

        results[key] = data_info

    return results


@app.get("/api/v1/appstore-iphone")
def appstore():
    country_codes = ["us", "de", "es", "in"]
    urls = {
        "free": {
            country: f"https://apps.apple.com/{country}/charts/iphone/top-free-apps/36"
            for country in country_codes
        },
        "paid": {
            country: f"https://apps.apple.com/{country}/charts/iphone/top-paid-apps/36"
            for country in country_codes
        },
    }

    results = {"free": {}, "paid": {}}

    for key, url_dict in urls.items():
        for country, url in url_dict.items():
            try:
                page = requests.get(url)
                page.raise_for_status()  # Raise an error for bad responses
                soup = BeautifulSoup(page.content, "html.parser")

                top_items = []
                chart_rows = soup.select("ol.l-row > li")

                for list_item in chart_rows[:25]:  # Limit to the first 25 items
                    copy = list_item.select_one("div.we-lockup__copy")
                    if copy:
                        id_tag = copy.select_one("p.we-lockup__rank")
                        app = copy.select_one("div.we-lockup__title")
                        by = copy.select_one("div.we-lockup__subtitle")
                        href = list_item.select_one("a.targeted-link")

                        overlay = list_item.select_one("div.we-lockup__overlay")
                        source_tag = overlay.find("source")

                        if id_tag and app and by and href:
                            id = int(id_tag.text.strip())
                            app_text = app.text.strip()
                            by_text = by.text.strip()
                            href_text = href.get("href")

                            if source_tag and "srcset" in source_tag.attrs:
                                srcset = source_tag["srcset"]
                                image = srcset.split(",")[0].split(" ")[
                                    0
                                ]  # Get the first URL
                            else:
                                image = "N/A"

                            top_items.append(
                                {
                                    "id": id,
                                    "image": image,
                                    "app": app_text,
                                    "by": by_text,
                                    "url": href_text,
                                }
                            )

                data_title = soup.select_one("h2.section__headline")
                results[key][country] = {
                    "data_title": data_title.text.strip() if data_title else "N/A",
                    "data": top_items,
                }
            except requests.RequestException as e:
                results = f"Error fetching data for {country} ({key}): {e}"
            except Exception as e:
                results = f"An error occurred while processing {country} ({key}): {e}"

    return results


@app.get("/api/v1/billboard-global-200")
def billboard():
    urls = {
        "music": "https://www.billboard.com/charts/billboard-global-200/",
    }

    results = {}

    for key, url in urls.items():
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        top_items = []

        # Use a more efficient way to select the top items
        chart_rows = soup.select("div.o-chart-results-list-row-container")

        for list_item in chart_rows[:25]:
            col1_item = list_item.select_one(
                f"li.o-chart-results-list__item:nth-of-type({1})"
            )
            if col1_item:
                id = int(col1_item.select_one("span.c-label").text.strip())

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

        # Extract metadata outside the loop
        data_title = (
            soup.select_one("h1.c-heading").text.strip()
            if soup.select_one("h1.c-heading")
            else "N/A"
        )
        data_desc = (
            soup.select("p.c-tagline")[0].text.strip()
            if soup.select("p.c-tagline")
            else "N/A"
        )

        nested_data = {
            "data_title": data_title,
            "data_desc": data_desc,
            "data": top_items,
        }

        results[key] = nested_data

    return results


@app.get("/api/v1/imdb")
def imdb():
    urls = {
        "movies": "https://www.imdb.com/chart/moviemeter/",
        "tv_shows": "https://www.imdb.com/chart/tvmeter/",
    }

    results = {}

    for key, url in urls.items():
        page = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(page.content, "html.parser")

        list_items = soup.select("li.ipc-metadata-list-summary-item")

        top_items = []
        for list_item in list_items[:25]:
            title = list_item.select_one("h3.ipc-title__text").text.strip()
            rank = int(
                list_item.select_one("div.meter-const-ranking").text.split(" ")[0]
            )

            year = (
                list_item.select_one(
                    "span.cli-title-metadata-item:nth-of-type(1)"
                ).text.replace("\u2013", "-")
                if list_item.select_one("span.cli-title-metadata-item:nth-of-type(1)")
                else "N/A"
            )
            length = (
                list_item.select_one(
                    "span.cli-title-metadata-item:nth-of-type(2)"
                ).text.strip()
                if list_item.select_one("span.cli-title-metadata-item:nth-of-type(2)")
                else "N/A"
            )
            age = (
                list_item.select_one(
                    "span.cli-title-metadata-item:nth-of-type(3)"
                ).text.strip()
                if list_item.select_one("span.cli-title-metadata-item:nth-of-type(3)")
                else "N/A"
            )

            rating_element = list_item.select_one("span.ipc-rating-star")
            if rating_element:
                rating_text = rating_element.text
                if "\xa0" in rating_text:
                    rating, num_votes = rating_text.split("\xa0")
                    num_votes = num_votes.strip("()")
                else:
                    rating = rating_text
                    num_votes = "N/A"
            else:
                rating, num_votes = "N/A", "N/A"

            href = (
                list_item.select_one("a.ipc-title-link-wrapper")["href"]
                if list_item.select_one("a.ipc-title-link-wrapper")
                else "N/A"
            )

            info = {
                "title": title,
                "rank": rank,
                "year": year,
                "length": length,
                "age": age,
                "href": href,
                "rating": rating,
                "num_votes": num_votes,
            }
            top_items.append(info)

        data_title = (
            soup.select_one("h1.ipc-title__text").text.strip()
            if soup.select_one("h1.ipc-title__text")
            else "N/A"
        )
        data_desc = (
            soup.select_one("div.ipc-title__description").text.strip()
            if soup.select_one("div.ipc-title__description")
            else "N/A"
        )

        nested_data = {
            "data_title": data_title,
            "data_desc": data_desc,
            "data": top_items,
        }

        results[key] = nested_data

    return results


@app.get("/api/v1/netflix-top-10")
def netflix():
    urls = {
        "movies": "https://www.netflix.com/tudum/top10",
        "tv_shows": "https://www.netflix.com/tudum/top10/tv",
    }

    results = {}

    for key, url in urls.items():
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        top_items = []
        table = soup.select_one("table")
        rows = table.select("tr")[1:]  # Skip the first row

        for row in rows:
            cells = row.find_all("td")
            rank = int(cells[0].text) if cells[0] else "N/A"
            title = cells[1].text.strip()

            if ": Season" in title:
                title_part, episode = title.split(": Season", 1)
                episode = "Season " + episode.strip()  # Retain "Season" keyword
            else:
                title_part = title
                episode = None

            title = title_part.strip()
            wks = int(cells[2].text) if cells[2] else "N/A"
            views = int(cells[5].text.replace(",", "")) if cells[5] else "N/A"

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
        data_info = {
            "data_title": data_title.text.strip(),
            "data_desc": data_desc.text.strip(),
            "data_updated": data_updated.text.strip(),
            "data": top_items,
        }

        results[key] = data_info

    return results


@app.get("/api/v1/steam-most-popular")
def steam():
    urls = {
        "games": "https://steamplayercount.com/popular",
    }

    results = {}

    for key, url in urls.items():
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        top_items = []
        table = soup.select_one("table")
        rows = table.select("tr")[1:]  # Skip the first row

        for row in rows[:25]:
            cells = row.find_all("td")

            img_tag = cells[0].find("img", class_="app-img") if cells[0] else "N/A"
            img = img_tag["src"] if img_tag and "src" in img_tag.attrs else "N/A"

            title = cells[1].text.strip() if cells[1] else "N/A"
            playercount = cells[2].text if cells[2] else "N/A"

            info = {
                "img": img,
                "title": title,
                "playercount": playercount,
            }
            top_items.append(info)

        data_title = soup.select_one("h1.title-big").text.strip()
        data_info = {
            "data_title": data_title,
            "data": top_items,
        }

        results[key] = data_info

    return results


serve()
