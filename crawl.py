from main import Crawler

c = Crawler()
c.go_to_page("https://www.google.com")
browser_content = "\n".join(c.crawl())

print(browser_content)
