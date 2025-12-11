from robocorp.tasks import task
from robocorp import browser, http
from RPA.Tables import Tables

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_website()

    orders = get_orders()
    for order in orders:
        fill_form(order)
        click_preview()
        submit_order()
    
def click_preview():
    page = browser.page()
    page.click("#preview")

def submit_order():
    page = browser.page()

    while True:
        page.click("#order")
        if page.query_selector("#receipt"):
            # success
            return
        if page.query_selector("#order-error"):
            print("[submit_order] Retrying")
            continue
        page.wait_for_timeout(300)


def fill_form(order):
    page = browser.page()
    page.select_option("#head", str(order["Head"]))

    body_selector = f"input[name='body'][value='{order['Body']}']"
    page.click(body_selector)

    legs_selector = "input[placeholder='Enter the part number for the legs']"
    page.fill(legs_selector, str(order["Legs"]))

    page.fill("#address", str(order["Address"]))

def get_orders():
    """
    Downloads the orders data and arranges it in a table format
    """
    http.download(
        url="https://robotsparebinindustries.com/orders.csv",
        path="output/orders.csv",
        overwrite=True
    )

    tables = Tables()
    orders_table = tables.read_table_from_csv("output/orders.csv")

    return orders_table

def open_robot_order_website():
    """
    Navigates to the given URL
    """
    browser.configure(
        slowmo = 10000,
    )
    order_page = browser.page()
    order_page.goto("https://robotsparebinindustries.com/#/robot-order")
    close_popup()

def close_popup():
    """
    Automatically closes pop up when website loads
    """
    page = browser.page()
    page.wait_for_selector(".btn.btn-dark", timeout=100)
    page.click(".btn.btn-dark")