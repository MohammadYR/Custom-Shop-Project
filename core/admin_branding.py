# import datetime
# from django.conf import settings
# from django.contrib import admin
# from django.utils.html import format_html


# BRAND_NAME  = getattr(settings, "BRAND_NAME", "فروشگاه کاستومی")
# APP_VERSION = getattr(settings, "APP_VERSION", "1.0.0")
# CURRENT_YEAR = datetime.date.today().year

# def create_badge(text, bg_color="#6c757d", text_color="#fff"):

#     style = (
#         f"display: inline-block; "
#         f"padding: 0.25em 0.6em; "
#         f"font-size: 0.75rem; "
#         f"font-weight: 600; "
#         f"line-height: 1; "
#         f"color: {text_color}; "
#         f"background-color: {bg_color}; "
#         f"border-radius: 0.375rem; "
#         f"margin-right: 10px;"
#     )
#     return format_html('<span style="{}">{}</span>', style, text)


# if settings.DEBUG:
#     env_badge = create_badge("محیط توسعه", bg_color="#dc3545")
# else:
#     env_badge = create_badge("پروداکشن", bg_color="#198754")


# admin.site.site_header = format_html(
#     "{}<strong style='letter-spacing:.5px;'>{}</strong> | {}",
#     env_badge,
#     BRAND_NAME,
#     "پنل مدیریت پیشرفته"
# )


# admin.site.site_title = f"{BRAND_NAME} | پنل ادمین"


# admin.site.index_title = format_html(
#     "به داشبورد مدیریتی {} خوش آمدید. <small style='color:#888'>(نسخه {})</small>",
#     BRAND_NAME,
#     APP_VERSION
# )


# admin.site.site_url = "/"