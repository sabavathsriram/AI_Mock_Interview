"""
Manual test runner for resume upload and document processing.
Tests all supported formats and validation scenarios.
"""

import asyncio
import httpx
import sys
import time
from pathlib import Path
from io import BytesIO
import uuid


BASE_URL = "http://localhost:8000/api/v1"
UPLOAD_DIR = Path("test_uploads")


class ResumeTestRunner:
    """Test runner for resume upload functionality."""
    
    def __init__(self):
        self.client = None
        self.auth_headers = None
        self.test_user_email = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "tests": []
        }
    
    async def setup(self):
        """Setup test client and authentication."""
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Create unique test user
        self.test_user_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        
        # Register user
        print(f"\n1. Registering test user: {self.test_user_email}")
        register_response = await self.client.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": self.test_user_email,
                "full_name": "Test User",
                "password": "TestPass123!"
            }
        )
        
        if register_response.status_code != 201:
            print(f"   [FAIL]: Registration failed: {register_response.text}")
            return False
        print("   [OK] User registered")
        
        # Login
        print("2. Logging in...")
        login_response = await self.client.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": self.test_user_email,
                "password": "TestPass123!"
            }
        )
        
        if login_response.status_code != 200:
            print(f"   [FAIL]: Login failed: {login_response.text}")
            return False
        
        token_data = login_response.json()
        self.auth_headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        print("   [OK] Login successful")
        
        return True
    
    async def teardown(self):
        """Cleanup."""
        if self.client:
            await self.client.aclose()
    
    def log_test(self, name, passed, message=""):
        """Log test result."""
        status = "[PASS]" if passed else "[FAIL]"
        print(f"   {status}: {name}")
        if message:
            print(f"      {message}")
        
        self.results["passed"] += 1 if passed else 0
        self.results["failed"] += 0 if passed else 1
        self.results["tests"].append({
            "name": name,
            "passed": passed,
            "message": message
        })
    
    async def test_supported_formats_info(self):
        """Test getting supported formats information."""
        print("\n" + "="*60)
        print("Testing Supported Formats Information")
        print("="*60)
        
        response = await self.client.get(f"{BASE_URL}/resumes/info/supported-formats")
        
        if response.status_code != 200:
            self.log_test("Get supported formats", False, f"Status {response.status_code}")
            return
        
        data = response.json()
        supported = data.get("supported_formats", [])
        unsupported = data.get("unsupported_formats", [])
        max_size = data.get("max_file_size_mb", 0)
        
        # Test passes if we got the data
        passed = len(supported) >= 8  # At least 8 supported formats
        self.log_test(
            "Get supported formats",
            passed,
            f"Found {len(supported)} supported formats, max size: {max_size}MB"
        )
        
        print(f"   Supported: {', '.join(supported[:5])}...")
        print(f"   Unsupported: {len(unsupported)} formats blocked")
    
    async def test_upload_txt(self):
        """Test uploading a TXT file."""
        print("\n" + "="*60)
        print("Testing TXT File Upload")
        print("="*60)
        
        content = """John Doe
Senior Software Engineer

Experience:
- 5 years as Senior Software Engineer at Tech Corp
- 3 years as Software Engineer at StartUp Inc

Skills:
- Python, Java, Go
- FastAPI, Django, Spring Boot
- MongoDB, PostgreSQL, Redis"""
        
        file_data = ("resume.txt", BytesIO(content.encode()), "text/plain")
        
        response = await self.client.post(
            f"{BASE_URL}/resumes/upload",
            files={"file": file_data},
            headers=self.auth_headers
        )
        
        passed = response.status_code == 201
        if passed:
            data = response.json()
            self.log_test(
                "Upload TXT file",
                True,
                f"File type: {data['file_type']}, Size: {data['file_size']} bytes"
            )
            return data.get("id")
        else:
            self.log_test("Upload TXT file", False, response.json().get("detail", "Unknown error"))
            return None
    
    async def test_upload_html(self):
        """Test uploading an HTML file."""
        print("\n" + "="*60)
        print("Testing HTML File Upload")
        print("="*60)
        
        content = """<!DOCTYPE html>
<html>
<head><title>Resume</title></head>
<body>
<h1>John Doe</h1>
<h2>Senior Software Engineer</h2>
<p>5+ years experience</p>
</body>
</html>"""
        
        file_data = ("resume.html", BytesIO(content.encode()), "text/html")
        
        response = await self.client.post(
            f"{BASE_URL}/resumes/upload",
            files={"file": file_data},
            headers=self.auth_headers
        )
        
        passed = response.status_code == 201
        self.log_test(
            "Upload HTML file",
            passed,
            response.json().get("detail") if not passed else "Success"
        )
        
        if passed:
            return response.json().get("id")
        return None
    
    async def test_upload_markdown(self):
        """Test uploading a Markdown file."""
        print("\n" + "="*60)
        print("Testing Markdown File Upload")
        print("="*60)
        
        content = """# John Doe

## Senior Software Engineer

### Experience
- 5 years at Tech Corp
- 3 years at StartUp Inc

### Skills
- Python, Java, Go"""
        
        file_data = ("resume.md", BytesIO(content.encode()), "text/markdown")
        
        response = await self.client.post(
            f"{BASE_URL}/resumes/upload",
            files={"file": file_data},
            headers=self.auth_headers
        )
        
        passed = response.status_code == 201
        self.log_test(
            "Upload Markdown file",
            passed,
            response.json().get("detail") if not passed else "Success"
        )
        
        if passed:
            return response.json().get("id")
        return None
    
    async def test_upload_rtf(self):
        """Test uploading an RTF file."""
        print("\n" + "="*60)
        print("Testing RTF File Upload")
        print("="*60)
        
        content = r"""{\rtf1\ansi\ansicpg1252
John Doe
Senior Software Engineer
Experience: 5+ years}"""
        
        file_data = ("resume.rtf", BytesIO(content.encode()), "application/rtf")
        
        response = await self.client.post(
            f"{BASE_URL}/resumes/upload",
            files={"file": file_data},
            headers=self.auth_headers
        )
        
        passed = response.status_code == 201
        self.log_test(
            "Upload RTF file",
            passed,
            response.json().get("detail") if not passed else "Success"
        )
        
        if passed:
            return response.json().get("id")
        return None
    
    async def test_upload_pdf(self):
        """Test uploading a PDF file."""
        print("\n" + "="*60)
        print("Testing PDF File Upload")
        print("="*60)
        
        try:
            from PyPDF2 import PdfWriter
            
            writer = PdfWriter()
            writer.add_blank_page(width=612, height=792)
            writer.add_metadata({
                '/Title': 'Resume',
                '/Author': 'John Doe',
            })
            
            output = BytesIO()
            writer.write(output)
            output.seek(0)
            
            file_data = ("resume.pdf", output, "application/pdf")
            
            response = await self.client.post(
                f"{BASE_URL}/resumes/upload",
                files={"file": file_data},
                headers=self.auth_headers
            )
            
            passed = response.status_code == 201
            self.log_test(
                "Upload PDF file",
                passed,
                response.json().get("detail") if not passed else "Success"
            )
            
            if passed:
                return response.json().get("id")
        except Exception as e:
            self.log_test("Upload PDF file", False, str(e))
        
        return None
    
    async def test_upload_docx(self):
        """Test uploading a DOCX file."""
        print("\n" + "="*60)
        print("Testing DOCX File Upload")
        print("="*60)
        
        try:
            from docx import Document
            
            doc = Document()
            doc.add_heading('John Doe', 0)
            doc.add_heading('Senior Software Engineer', level=1)
            doc.add_paragraph('5+ years experience', style='List Bullet')
            
            output = BytesIO()
            doc.save(output)
            output.seek(0)
            
            file_data = ("resume.docx", output, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            
            response = await self.client.post(
                f"{BASE_URL}/resumes/upload",
                files={"file": file_data},
                headers=self.auth_headers
            )
            
            passed = response.status_code == 201
            self.log_test(
                "Upload DOCX file",
                passed,
                response.json().get("detail") if not passed else "Success"
            )
            
            if passed:
                return response.json().get("id")
        except Exception as e:
            self.log_test("Upload DOCX file", False, str(e))
        
        return None
    
    async def test_unsupported_jpg(self):
        """Test rejection of JPG file."""
        print("\n" + "="*60)
        print("Testing Unsupported Format Rejection (JPG)")
        print("="*60)
        
        jpg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100
        file_data = ("image.jpg", BytesIO(jpg_data), "image/jpeg")
        
        response = await self.client.post(
            f"{BASE_URL}/resumes/upload",
            files={"file": file_data},
            headers=self.auth_headers
        )
        
        passed = response.status_code == 400
        self.log_test(
            "Reject JPG file",
            passed,
            f"Status {response.status_code}: {response.json().get('detail', 'N/A')}"
        )
    
    async def test_unsupported_png(self):
        """Test rejection of PNG file."""
        print("\n" + "="*60)
        print("Testing Unsupported Format Rejection (PNG)")
        print("="*60)
        
        png_data = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        file_data = ("image.png", BytesIO(png_data), "image/png")
        
        response = await self.client.post(
            f"{BASE_URL}/resumes/upload",
            files={"file": file_data},
            headers=self.auth_headers
        )
        
        passed = response.status_code == 400
        self.log_test(
            "Reject PNG file",
            passed,
            f"Status {response.status_code}"
        )
    
    async def test_unsupported_zip(self):
        """Test rejection of ZIP file."""
        print("\n" + "="*60)
        print("Testing Unsupported Format Rejection (ZIP)")
        print("="*60)
        
        import zipfile
        
        output = BytesIO()
        with zipfile.ZipFile(output, 'w') as zf:
            zf.writestr('test.txt', 'test')
        output.seek(0)
        
        file_data = ("archive.zip", output, "application/zip")
        
        response = await self.client.post(
            f"{BASE_URL}/resumes/upload",
            files={"file": file_data},
            headers=self.auth_headers
        )
        
        passed = response.status_code == 400
        self.log_test(
            "Reject ZIP file",
            passed,
            f"Status {response.status_code}"
        )
    
    async def test_unsupported_exe(self):
        """Test rejection of EXE file."""
        print("\n" + "="*60)
        print("Testing Unsupported Format Rejection (EXE)")
        print("="*60)
        
        exe_data = b'MZ' + b'\x00' * 100
        file_data = ("program.exe", BytesIO(exe_data), "application/x-msdownload")
        
        response = await self.client.post(
            f"{BASE_URL}/resumes/upload",
            files={"file": file_data},
            headers=self.auth_headers
        )
        
        passed = response.status_code == 400
        self.log_test(
            "Reject EXE file",
            passed,
            f"Status {response.status_code}"
        )
    
    async def test_list_resumes(self, resume_id):
        """Test listing resumes."""
        print("\n" + "="*60)
        print("Testing Resume Listing")
        print("="*60)
        
        response = await self.client.get(
            f"{BASE_URL}/resumes/list",
            headers=self.auth_headers
        )
        
        passed = response.status_code == 200
        if passed:
            data = response.json()
            self.log_test(
                "List resumes",
                True,
                f"Found {data['total_count']} resumes"
            )
        else:
            self.log_test("List resumes", False, response.json().get("detail"))
    
    async def test_get_resume_details(self, resume_id):
        """Test getting resume details."""
        print("\n" + "="*60)
        print("Testing Resume Details Retrieval")
        print("="*60)
        
        if not resume_id:
            self.log_test("Get resume details", False, "No resume ID provided")
            return
        
        response = await self.client.get(
            f"{BASE_URL}/resumes/{resume_id}",
            headers=self.auth_headers
        )
        
        passed = response.status_code == 200
        if passed:
            data = response.json()
            self.log_test(
                "Get resume details",
                True,
                f"File: {data['filename']}, Type: {data['file_type']}"
            )
        else:
            self.log_test("Get resume details", False, response.json().get("detail"))
    
    async def test_delete_resume(self, resume_id):
        """Test deleting a resume."""
        print("\n" + "="*60)
        print("Testing Resume Deletion")
        print("="*60)
        
        if not resume_id:
            self.log_test("Delete resume", False, "No resume ID provided")
            return
        
        response = await self.client.delete(
            f"{BASE_URL}/resumes/{resume_id}",
            headers=self.auth_headers
        )
        
        passed = response.status_code == 200
        self.log_test(
            "Delete resume",
            passed,
            response.json().get("message", "N/A") if passed else response.json().get("detail")
        )
    
    async def run_all_tests(self):
        """Run all tests."""
        print("\n" + "="*80)
        print("RESUME UPLOAD AND DOCUMENT PROCESSING TEST SUITE")
        print("="*80)
        
        # Setup
        if not await self.setup():
            print("\n[ERROR] Setup failed. Exiting.")
            return False
        
        try:
            # Test supported formats info
            await self.test_supported_formats_info()
            
            # Test supported formats
            txt_id = await self.test_upload_txt()
            await self.test_upload_html()
            await self.test_upload_markdown()
            await self.test_upload_rtf()
            await self.test_upload_pdf()
            await self.test_upload_docx()
            
            # Test unsupported formats
            await self.test_unsupported_jpg()
            await self.test_unsupported_png()
            await self.test_unsupported_zip()
            await self.test_unsupported_exe()
            
            # Test resume management
            await self.test_list_resumes(txt_id)
            if txt_id:
                await self.test_get_resume_details(txt_id)
                # Delete the last uploaded file
                await self.test_delete_resume(txt_id)
            
        finally:
            await self.teardown()
        
        # Print summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Passed: {self.results['passed']}")
        print(f"Failed: {self.results['failed']}")
        print(f"Total:  {self.results['passed'] + self.results['failed']}")
        
        if self.results['failed'] == 0:
            print("\n[SUCCESS] ALL TESTS PASSED!")
            return True
        else:
            print(f"\n[FAILED] {self.results['failed']} TEST(S) FAILED")
            return False


async def main():
    """Main entry point."""
    runner = ResumeTestRunner()
    success = await runner.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Error running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
