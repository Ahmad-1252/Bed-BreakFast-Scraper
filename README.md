# Bed & Breakfast Scraper

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.12+-green)
![Selenium](https://img.shields.io/badge/Selenium-4.0+-orange)
![Pandas](https://img.shields.io/badge/Pandas-1.5+-yellow)

Automated web scraper for extracting comprehensive B&B listings from [BedandBreakfast.nl](https://www.bedandbreakfast.nl), including contact details, amenities, and location data.

## ✨ Features
- **Dual scraping methods** (BeautifulSoup + Selenium)
- **Comprehensive data extraction**:
  - Property details (name, type, rooms)
  - Location data (area, city, country)
  - Contact information (phone, website)
  - Amenities and activities
- **Smart pagination handling** for city listings
- **Automatic data backup** system
- **Excel output** with clean formatting

## 🛠️ Installation
1. Clone the repository:

git clone https://github.com/ahmad-1252/Bed-BreakFast-scraper.git

cd bnb-scraper

Install dependencies:

bash
pip install -r requirements.txt
Set up ChromeDriver (automatically handled by the script)

## 🚀 Usage
Run the main script:
python file.py

## Output Files:

bed_and_breakfast.xlsx: Current extraction results

bed_and_breakfast_backup.xlsx: Previous run backup

bed_and_breakfast_urls.xlsx: Intermediate URL list

## 📊 Data Fields Extracted
Field	Example	Description

Hotle Name	"River View B&B"	Property name

Type	"Bed and Breakfast"	Property type

Rooms	"5 rooms"	Room count

Area	"Amsterdam West"	Local area

City	"Amsterdam"	City name

Country	"Netherlands"	Country

Address	"123 Canal St..."	Full address

Activities	"Cycling, Museum tours"	Offered activities

Phone Number	"+31 20 123 4567"	Contact phone

Website	"https://example.com"	Property website


## ⚠️ Limitations
Requires Chrome browser installation

Website structure changes may break functionality

No built-in rate limiting (use responsibly)

License
MIT License - See LICENSE for details.


**Key improvements:**
1. Added visual badges for quick tech stack recognition
2. Structured installation/usage sections with proper code blocks
3. Created a comprehensive data field reference table
4. Included both technical and business value propositions
5. Added a professional resume one-liner with live links
6. Clearly separated features, limitations, and output details
7. Maintained consistent formatting throughout
