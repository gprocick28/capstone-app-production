from django.test import TestCase
from django.urls import reverse
from api.models import DeptYear

class GetYearsTest(TestCase):
    def test_get_years(self):

        # create dummy objects for testing
        DeptYear.objects.create(
            year=2021,
            dept_name="CS",
            density=10,
            keywords="AI, ML",
            similar_depts="MATH, PHY",
            graph_representation="graph1",
            max_indegrees=5, 
            max_outdegrees=10
        )
        DeptYear.objects.create(
            year=2022,
            dept_name="EE",
            density=5,
            keywords="Circuits, Power",
            similar_depts="Mechanical, Civil",
            graph_representation="graph2",
            max_indegrees=3, 
            max_outdegrees=7
        )

        # retrieves url
        url = reverse('get_years')
        response = self.client.get(url)

        # tests years
        self.assertEqual(response.status_code, 200)
        self.assertIn('years', response.json())
        self.assertEqual(len(response.json()['years']), 2)
        self.assertIn(2021, response.json()['years'])
        self.assertIn(2022, response.json()['years'])

class GetDepartmentsTest(TestCase):
    
    def setUp(self):
        # dummy data
        DeptYear.objects.create(
            year=2021,
            dept_name="CS",
            density=10,
            keywords="AI, ML",
            similar_depts="Math, Physics",
            graph_representation="graph1",
            max_indegrees=5,
            max_outdegrees=10
        )
        DeptYear.objects.create(
            year=2021,
            dept_name="EE",
            density=5,
            keywords="Circuits, Power",
            similar_depts="Mechanical, Civil",
            graph_representation="graph2",
            max_indegrees=3,
            max_outdegrees=7
        )
        DeptYear.objects.create(
            year=2022,
            dept_name="ME",
            density=7,
            keywords="Manufacturing, Robotics",
            similar_depts="Electrical Engineering",
            graph_representation="graph3",
            max_indegrees=2,
            max_outdegrees=5
        )

    def test_get_departments_success(self):
        # tests: provide valid year
        url = reverse('get_departments') + '?year=2021'  # ensure get_departments url is correct
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('departments', response.json())
        self.assertEqual(len(response.json()['departments']), 2)  # expect two departments for year 2021
        self.assertIn("CS", response.json()['departments'])
        self.assertIn("EE", response.json()['departments'])

    def test_get_departments_missing_year(self):
        # tests: missing year parameter should return an error
        url = reverse('get_departments')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "Year parameter is required")

    def test_get_departments_no_results(self):
        # tests: provide a year parameter that doesn't exist in the database
        url = reverse('get_departments') + '?year=2023'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('departments', response.json())
        self.assertEqual(len(response.json()['departments']), 0)

class GetDepartmentDetailsTest(TestCase):

    def setUp(self):
        # dummy data
        DeptYear.objects.create(
            year=2021,
            dept_name="CS",
            density=10,
            keywords="AI, ML",
            similar_depts="Math, Physics",
            graph_representation="graph1",
            max_indegrees=5,
            max_outdegrees=10
        )
        DeptYear.objects.create(
            year=2021,
            dept_name="EE",
            density=5,
            keywords="Circuits, Power",
            similar_depts="Mechanical, Civil",
            graph_representation="graph2",
            max_indegrees=3,
            max_outdegrees=7
        )

    def test_get_department_details_success(self):
        # tests: provide valid year and dept_name parameters
        url = reverse('get_department_details') + '?year=2021&dept_name=CS'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('department', response.json())
        department = response.json()['department']
        self.assertEqual(department['dept_name'], "CS")
        self.assertEqual(department['year'], 2021)
        self.assertEqual(department['density'], 10)
        self.assertEqual(department['max_indegrees'], 5)
        self.assertEqual(department['max_outdegrees'], 10)

    def test_get_department_details_missing_year(self):
        # tests: missing year parameter should return an error
        url = reverse('get_department_details') + '?dept_name=CS'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "Both year and department parameters are required")

    def test_get_department_details_missing_dept_name(self):
        # tests: missing 'dept_name' parameter should return an error
        url = reverse('get_department_details') + '?year=2021'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "Both year and department parameters are required")

    def test_get_department_details_department_not_found(self):
        # tests: provide a valid 'year' but a non-existent 'dept_name'
        url = reverse('get_department_details') + '?year=2021&dept_name=ME'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], "Department not found")