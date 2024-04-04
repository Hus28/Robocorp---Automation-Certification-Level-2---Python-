from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
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
    browser.configure(
        slowmo=0,
    )
    open_website()
    orders = get_orders()
    for order in orders:
        close_annoying_modal()
        order_robot(order)
    
    archive_receipts()


def open_website():
    """Navigates to given URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():
    """Get orders"""

    """Downloads CSV file with order information"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

    """Reads CSV into table"""
    library = Tables()
    orders = library.read_table_from_csv(
        "orders.csv", columns=["Order number", "Head", "Body", "Legs", "Address"]
    )

    return orders

def order_robot(order):
    """Orders a robot with information from orders table"""
    print(order)
    fill_the_form(order)

def close_annoying_modal():
    """Closes the annoying modal while opening the website"""
    page = browser.page()
    page.click("button:text('OK')")

def store_receipt_as_pdf(order_number):
    """Stores the order receipt as PDF"""
    page = browser.page()
    page.pdf(
        path=f"output/order_receipt_{order_number}.pdf",
        scale=0.5,
        print_background=True,
    )
    return f"output/order_receipt_{order_number}.pdf"

def screenshot_robot(order_number):
    """Takes a screenshot of the ordered robot"""
    page = browser.page()
    page.screenshot(
        path=f"output/robot_{order_number}.png",
        full_page=True,
    )

    return f"output/robot_{order_number}.png"

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embeds the screenshot to the PDF receipt"""
    pdf = PDF()
    pdf.add_files_to_pdf(
        files=[pdf_file,screenshot],
        target_document=pdf_file
    )

def fill_the_form(order):
    """Fills the form with the given data from table"""
    page = browser.page()

    # Select Head
    page.select_option("#head", str(order["Head"]))

    # Select Body
    selector = f"#id-body-{order['Body']}"
    page.click(selector)

    # Select Legs
    page.get_by_placeholder("Enter the part number for the legs").fill(str(order["Legs"]))

    # Fill in the address
    page.fill("#address", str(order["Address"]))

    # Get preview of the robot
    page.click("button:text('Preview')")

    # Submit the order
    while True:
        page.click("button:text('Order')")

        # Check for the presence of the alert
        if page.query_selector(".alert.alert-danger"):
            # If alert is present, click the "Order" button again
            continue
        else:
            # If no alert, break the loop
            break

    # Save the order receipt as PDF
    pdf = store_receipt_as_pdf(order['Order number'])

    # Take a screenshot of the ordered robot
    screenshot = screenshot_robot(order['Order number'])

    # Embed the screenshot to the PDF receipt
    embed_screenshot_to_receipt(screenshot, pdf)

    # Order next robot
    page.click("button:text('Order another robot')")

def archive_receipts():
    """Creates ZIP archive of the receipts and the images"""
    library = Archive()

    library.archive_folder_with_zip('./output', 'all_my_robot_orders.zip')