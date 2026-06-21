from pypdf import PdfReader

reader = PdfReader("docs/research/electricity.pdf")
print(f"Pages: {len(reader.pages)}")
for i in range(len(reader.pages)):
    print(f"--- Page {i + 1} ---")
    print(reader.pages[i].extract_text())
