from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
import re

class HelpPageTests(TestCase):
    def setUp(self):
        """Set up test client and create test user"""
        self.client = Client()
        self.help_url = reverse('help')
        self.quiz_list_url = reverse('quiz_list')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_help_page_url_exists(self):
        """Test that help page URL exists and returns 200 status code"""
        response = self.client.get(self.help_url)
        self.assertEqual(response.status_code, 200)

    def test_help_page_uses_correct_template(self):
        """Test that help page uses the correct template"""
        response = self.client.get(self.help_url)
        self.assertTemplateUsed(response, 'quiz/help.html')
        self.assertTemplateUsed(response, 'quiz/base.html')

    def test_help_page_content(self):
        """Test that help page contains expected content"""
        response = self.client.get(self.help_url)
        content = response.content.decode('utf-8')
        
        # Test section headings exist
        self.assertIn('Quick Start Guide', content)
        self.assertIn('Frequently Asked Questions', content)
        self.assertIn('Tips & Support', content)
        self.assertIn('Additional Resources', content)

        # Test specific content elements
        self.assertIn('Register/Login', content)
        self.assertIn('Choose a Quiz', content)
        self.assertIn('Take the Quiz', content)
        self.assertIn('Review Results', content)

    def test_official_dvs_links_present(self):
        """Test that all official DVS links are present and correctly formatted"""
        response = self.client.get(self.help_url)
        content = response.content.decode('utf-8')
        
        # List of required DVS links
        dvs_links = [
            'https://drive.mn.gov/',
            'https://dps.mn.gov/divisions/dvs/forms-documents/Documents/Minnesota_Drivers_Manual.pdf',
            'https://onlineservices.dps.mn.gov/EServices/_/',
            'https://dps.mn.gov/divisions/dvs/locations/Pages/find-office-locations.aspx'
        ]
        
        # Check each link exists and has proper attributes
        for link in dvs_links:
            # Check link href exists
            self.assertIn(f'href="{link}"', content)
            # Check target="_blank" and rel="noopener noreferrer" for security
            link_pattern = f'href="{link}"[^>]*target="_blank"[^>]*rel="noopener noreferrer"'
            self.assertTrue(re.search(link_pattern, content), 
                          f"Link {link} missing security attributes")

    def test_study_materials_links_present(self):
        """Test that all study material links are present and correctly formatted"""
        response = self.client.get(self.help_url)
        content = response.content.decode('utf-8')
        
        # List of required study material links
        study_links = [
            'https://dps.mn.gov/divisions/dvs/forms-documents/Documents/Minnesota_Road_Signs.pdf',
            'https://dps.mn.gov/divisions/dvs/news/Pages/default.aspx',
            'https://dps.mn.gov/divisions/dvs/forms-documents/Pages/drivers-manuals.aspx',
            'https://dps.mn.gov/divisions/dvs/Pages/drivers-license-information.aspx'
        ]
        
        # Check each link exists and has proper attributes
        for link in study_links:
            # Check link href exists
            self.assertIn(f'href="{link}"', content)
            # Check target="_blank" and rel="noopener noreferrer" for security
            link_pattern = f'href="{link}"[^>]*target="_blank"[^>]*rel="noopener noreferrer"'
            self.assertTrue(re.search(link_pattern, content), 
                          f"Link {link} missing security attributes")

    def test_support_contact_information(self):
        """Test that support contact information is present and correct"""
        response = self.client.get(self.help_url)
        content = response.content.decode('utf-8')
        
        # Test support section exists
        self.assertIn('Need More Help?', content)
        
        # Test support email is correct
        support_email = 'support@mnpracticetest.com'
        self.assertIn(f'href="mailto:{support_email}"', content)
        self.assertIn(support_email, content)

    def test_resource_icons_present(self):
        """Test that appropriate icons are present for resources"""
        response = self.client.get(self.help_url)
        content = response.content.decode('utf-8')
        
        # List of required icons
        icons = [
            'fa-external-link-alt',  # For external links
            'fa-book',               # For study materials
            'fa-graduation-cap',     # For manuals and guides
            'fa-car'                 # For license information
        ]
        
        # Check each icon exists
        for icon in icons:
            self.assertIn(f'fas {icon}', content)

    def test_section_organization(self):
        """Test that resources are properly organized in sections"""
        response = self.client.get(self.help_url)
        content = response.content.decode('utf-8')
        
        # Test main section headers
        sections = [
            'Official Minnesota DVS Resources',
            'Study Materials'
        ]
        
        for section in sections:
            self.assertIn(section, content)
            
        # Test proper nesting of sections in columns
        self.assertIn('col-md-6', content)
        
    def test_link_descriptions(self):
        """Test that links have descriptive text"""
        response = self.client.get(self.help_url)
        content = response.content.decode('utf-8')
        
        # List of required link descriptions
        descriptions = [
            'Minnesota Driver and Vehicle Services (DVS)',
            'Minnesota Driver\'s Manual (PDF)',
            'Schedule Your Actual Test',
            'Find DVS Office Locations',
            'Road Signs Guide (PDF)',
            'Latest DVS Updates & News',
            'All Driver Manuals & Guides',
            'License Requirements & Classes'
        ]
        
        # Check each description exists
        for desc in descriptions:
            self.assertIn(desc, content)

    def test_security_headers(self):
        """Test that security headers are present in the response"""
        response = self.client.get(self.help_url)
        
        # Test for common security headers
        security_headers = [
            'X-Frame-Options',
            'X-Content-Type-Options',
            'X-XSS-Protection'
        ]
        
        for header in security_headers:
            self.assertIn(header, response.headers)

    def test_responsive_design_elements(self):
        """Test that responsive design elements are present"""
        response = self.client.get(self.help_url)
        content = response.content.decode('utf-8')
        
        # Test responsive classes
        responsive_classes = [
            'container',
            'row',
            'col-md-6',
            'card'
        ]
        
        for class_name in responsive_classes:
            self.assertIn(class_name, content)

    def test_help_page_accessible_when_logged_in(self):
        """Test that help page is accessible when user is logged in"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.help_url)
        self.assertEqual(response.status_code, 200)

    def test_help_page_accessible_when_logged_out(self):
        """Test that help page is accessible when user is not logged in"""
        response = self.client.get(self.help_url)
        self.assertEqual(response.status_code, 200)

    def test_navigation_links_present(self):
        """Test that navigation links are present in the template"""
        response = self.client.get(self.help_url)
        content = response.content.decode('utf-8')
        
        # Test navigation menu items
        self.assertIn('fa-question-circle', content)  # Help icon
        self.assertIn('fa-home', content)  # Home icon
        self.assertIn('href="/help/"', content)  # Help link
        self.assertIn('href="/"', content)  # Home link

    def test_ui_elements_present(self):
        """Test that UI elements are present"""
        response = self.client.get(self.help_url)
        content = response.content.decode('utf-8')
        
        # Test card elements
        self.assertIn('card-header', content)
        self.assertIn('card-body', content)
        
        # Test accordion elements for FAQ
        self.assertIn('accordion', content)
        self.assertIn('accordion-button', content)
        
        # Test footer
        self.assertIn('Practice for your Minnesota Driver\'s License Test', content)

    def test_help_link_from_home(self):
        """Test that help page is accessible from home page"""
        response = self.client.get(self.quiz_list_url)
        content = response.content.decode('utf-8')
        
        # Test Learn More button presence
        self.assertIn('Learn More', content)
        self.assertIn('href="/help/"', content)

    def test_responsive_layout(self):
        """Test that responsive classes are present"""
        response = self.client.get(self.help_url)
        content = response.content.decode('utf-8')
        
        # Test responsive classes
        self.assertIn('container', content)
        self.assertIn('row', content)
        self.assertIn('col-md-4', content)
        self.assertIn('navbar-expand-lg', content)
        self.assertIn('navbar-toggler', content)

    def test_help_link_in_navigation(self):
        """Test that help link appears in navigation"""
        response = self.client.get(self.help_url)  # Get help page instead of home page
        content = response.content.decode('utf-8')
        # Check for both the link text and the icon
        self.assertIn('fa-question-circle', content)
        self.assertIn('Help', content)
