app_name = "miraihr_core"
app_title = "MiraiHR"
app_publisher = "MiraiHR"
app_description = "MiraiHR product branding and employee entry point"
app_email = "support@miraihr.example"
app_license = "UNLICENSED"
app_logo_url = "/assets/miraihr_core/images/miraihr-mark.svg"
app_home = "/app/miraihr-home"

brand_html = (
    '<a class="miraihr-login-brand" href="/" aria-label="MiraiHR home">'
    '<img src="/assets/miraihr_core/images/miraihr-mark.svg" alt="MiraiHR">'
    "<span>MiraiHR</span></a>"
)

app_include_css = "/assets/miraihr_core/css/miraihr.css"
web_include_css = ["/assets/miraihr_core/css/miraihr.css"]

add_to_apps_screen = [
    {
        "name": "miraihr_core",
        "logo": app_logo_url,
        "title": "MiraiHR",
        "route": app_home,
        "has_permission": "miraihr_core.permissions.has_core_access",
        "sequence_id": 10,
    }
]
