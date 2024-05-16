from func.example import PingCog
from func.note import NoteCog
from func.calendar import CalendarCog
from func.spending import SpendingCog

BOT_AUTHORIZE_TOKEN=""
BOT_COMMAND_PREFIX="!"

BOT_CONFIG_LIST = [PingCog, NoteCog, CalendarCog, SpendingCog]