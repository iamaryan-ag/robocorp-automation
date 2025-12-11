from robocorp.tasks import task
from robocorp import browser, http
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

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
        ss_path = screenshot_robot(order["Order number"])
        pdf_path = store_receipt_as_pdf(order["Order number"])
        final_pdf = embed_screenshot_to_receipt(ss_path, pdf_path)
        browser.page().click("#order-another")
        close_popup()
    archive_receipts()

def archive_receipts():
    archive = Archive()
    archive.archive_folder_with_zip(
        folder="output/receipts",
        archive_name="output/receipts.zip"
    )

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    output_path = pdf_file
    pdf.add_watermark_image_to_pdf(
        image_path=screenshot,
        source_path=pdf_file,
        output_path=output_path
    )
    return output_path

def screenshot_robot(order_number):
    page = browser.page()
    robot_img = page.locator("#robot-preview-image")
    robot_img.screenshot(path=f"output/screenshots/robot_{order_number}.png")
    return f"output/screenshots/robot_{order_number}.png"

def store_receipt_as_pdf(order_number):
    page = browser.page()
    pdf = PDF()
    receipt_html = page.locator("#receipt").inner_html()
    pdf.html_to_pdf(receipt_html, f"output/receipts/receipt_{order_number}.pdf")
    return f"output/receipts/receipt_{order_number}.pdf"

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