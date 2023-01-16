CAPTION = \
    """By @{}

tag us to be posted @{}"""

HASHTAGS = "#likeback #likesforlikes #likes4likes #outfitoftheday #followback #stylish #likes #lookbook #likeforlikes " \
           "#drip #like4follow #instastyle #driplife #lookoftheday #like4likes #recent4recent #spamforspam #spam4spam " \
           "#fashiongram #look #menswear #shoes #recentforrecent #fashiondiaries #fashionpost #ejuice #wiwt " \
           "#whatiwore #cloudchaser #subohm"

COMMENTS_TEMPLATES = ["🔥🔥", "this is drip 🔥🔥", "Nice one 🔥🔥", "2 hot 🔥🔥", "💎💎", "🥶🥶🥶", "🚀🚀", "🔞🔞",
                      "fuckkkk 🔥", "💧💧", "drip 💧", "2 hard 🔥", "🥶", "💙💙💙", "❤️", "🤙",
                      "Nice💙", "💪💪", "amazing🔥", "🔥", "💙", "🚀"]

ACCOUNTS_TO_FOLLOW_PER_DAY = [20, 40]
ACCOUNTS_TO_LIKE_PER_DAY = [60, 80]
ACCOUNTS_TO_COMMENT_PER_DAY = [10, 20]

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
