from selenium import webdriver


class PathTo:
    DOWNLOAD = "photos/"
    SOURCE_TRAFFIC_PEOPLE = "source_traffic_accounts/people.txt"
    SOURCE_TRAFFIC_GROUPS = "source_traffic_accounts/groups.txt"
    USED_USERS = "used_users.txt"
    CHROME_DRIVER_PATH = 'chromedriver.exe'


CAPTION = \
    """By @{}

tag us to be posted @{}"""

HASHTAGS = "#likeback #likesforlikes #likes4likes #outfitoftheday #followback #stylish #likes #lookbook #likeforlikes " \
           "#drip #like4follow #instastyle #driplife #lookoftheday #like4likes #recent4recent #spamforspam #spam4spam " \
           "#fashiongram #look #menswear #shoes #recentforrecent #fashiondiaries #fashionpost #ejuice #wiwt " \
           "#whatiwore #cloudchaser #subohm"

COMMENTS_TEMPLATES = ["🔥🔥", "this is drip 🔥🔥", "Nice one 🔥🔥", "2 hot 🔥🔥", "💎💎", "🥶🥶🥶", "🚀🚀", "🔞🔞",
                      "fuckkk 🔥", "💧💧", "drip 💧💧", "2 hard 💧💧", "🥶", "💙💙💙", "❤️", "🤙",
                      "Nice 💙💙", "💪💪", "amazing🔥", "🔥", "💙", "🚀"]

ID_TELEGRAM_CHAT = 1736337003

ACCOUNTS_TO_FOLLOW_PER_DAY = [20, 40]
ACCOUNTS_TO_LIKE_PER_DAY = [60, 80]
ACCOUNTS_TO_COMMENT_PER_DAY = [10, 20]


class ScrapeSettings:
    HOURS_TO_WORK = 14

    MAX_USER_TO_INTERACT = ACCOUNTS_TO_FOLLOW_PER_DAY[1] + ACCOUNTS_TO_COMMENT_PER_DAY[1] + ACCOUNTS_TO_LIKE_PER_DAY[
        1]

    # People and Groups
    PARSING_SOURCE = 2

    # Followers, Likes and Tags
    GROUPS_PARSING_CATEGORIES = 3
    # Followers and Likes
    PEOPLE_PARSING_CATEGORIES = 2

    GROUPS_TO_CHECK = 10
    PEOPLE_TO_CHECK = 10

    NUM_TO_REQUEST_PER_CATEGORY_GROUPS = (
            ((MAX_USER_TO_INTERACT // PARSING_SOURCE) // GROUPS_TO_CHECK) // GROUPS_PARSING_CATEGORIES)
    NUM_TO_REQUEST_PER_CATEGORY_PEOPLE = (
            ((MAX_USER_TO_INTERACT // PARSING_SOURCE) // PEOPLE_TO_CHECK) // PEOPLE_PARSING_CATEGORIES)


class HashtagsGen:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    URL = "https://displaypurposes.com/"
