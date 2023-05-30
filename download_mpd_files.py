from bs4 import BeautifulSoup
import json
import os


def main():
    with open("downloads/mpd_urls_cleaned.json", "r") as urls_file:
        topics = json.load(urls_file)
    urls_file.close()

    # unique_urls = set()
    # topics_cleaned = dict()

    # for key in topics:
    #     for url in topics[key]:
    #         if not url in unique_urls:
    #             if topics_cleaned.get(key, None) is None:
    #                 topics_cleaned[key] = [url]
    #             else:
    #                 topics_cleaned[key].append(url)
    #             unique_urls.add(url)

    # with open("downloads/mpd_urls_cleaned.json", "w") as cleaned_urls:
    #     cleaned_urls.write(json.dumps(topics_cleaned, ensure_ascii=False))

    for counter, topic in enumerate(topics):
        for i, url in enumerate(topics[topic]):
            os.system("curl {} -o downloads/master.mpd".format(url))

            with open("downloads/master.mpd", "r") as master_mpd:
                data = master_mpd.read()
            master_mpd.close()

            bs_data = BeautifulSoup(data, "xml")

            with open("downloads/master_edited.mpd", "w") as master_edited_mpd:
                master_edited_mpd.write(bs_data.prettify())
            master_edited_mpd.close()

            os.system(
                'streamlink -o downloads/videos/"{video_name}.mp4" {mpd_file} 720p -n'.format(
                    mpd_file="file:///Users/intizar/MyWorld/ovadan-scraping/downloads/master_edited.mpd",
                    video_name=topic + " - video-" + str(i + 1),
                )
            )


if __name__ == "__main__":
    main()
