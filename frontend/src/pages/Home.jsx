import { useState, useEffect, useRef } from "react";
import api from "../api";
import 'bootstrap/dist/css/bootstrap.min.css';
import Dropdown from 'react-bootstrap/Dropdown';
import DropdownButton from 'react-bootstrap/DropdownButton';
import { Button } from 'react-bootstrap';
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import Image from 'react-bootstrap/Image';
import Accordion from 'react-bootstrap/Accordion';
import cytoscape from "cytoscape";
import dagre from "cytoscape-dagre";

function Home() {
  // useState is used for variables so that data persists between renders
  const [selectedUniversity, setSelectedUniversity] = useState("Select University");

  const [years, setYears] = useState([]);
  const [selectedYear, setSelectedYear] = useState("Select Year");

  const [departments, setDepartments] = useState([]);
  const [selectedDepartment, setSelectedDepartment] = useState("Select Department");

  const [departmentDetails, setDepartmentDetails] = useState(null);

  const cytoscapeGraphRef = useRef(null); // stores variables between renders, does not re-render when updated (unlike useState)

  // gets yeaars
  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/years/")
      .then(response => response.json())
      .then(data => setYears(data.years))
      .catch(error => console.error("Error fetching years:", error));
  }, []);

  // gets departments for selected year if a year is selected
  useEffect(() => {
    if (selectedYear !== "Select Year") {
      fetch(`http://127.0.0.1:8000/api/departments/?year=${selectedYear}`)
        .then(response => response.json())
        .then(data => setDepartments(data.departments))
        .catch(error => console.error("Error fetching departments:", error));
    }
  }, [selectedYear]);

  // gets department details if year and department are selected
  useEffect(() => {
    if (selectedYear !== "Select Year" && selectedDepartment !== "Select Department") {
      fetch(`http://127.0.0.1:8000/api/department_details/?year=${selectedYear}&dept_name=${selectedDepartment}`)
        .then(response => response.json())
        .then(data => {
          if (data.department) {
            setDepartmentDetails(data.department);
          } else {
            console.error("Error fetching department details:", data.error);
            setDepartmentDetails(null);
          }
        })
        .catch(error => console.error("Error fetching department details:", error));
    }
  }, [selectedYear, selectedDepartment]);

  useEffect(() => {

    // Fixes formatting issues inside the CSV
    function fixToJson(str) {
      str = str.trim();
      if (str.startsWith('elements:')) str = str.replace('elements:', '').trim();
      str = str.replace(/'/g, '"');
      str = str.replace(/([{,]\s*)(\w+)\s*:/g, '$1"$2":');
      return str;
    }

    if (selectedYear !== "Select Year" && selectedDepartment !== "Select Department") {
      if (departmentDetails?.graph_representation) {
        cytoscape.use(dagre);

        var graphText = fixToJson(departmentDetails.graph_representation); // clean up graph JSON text
        const elements = JSON.parse(graphText);  // turn text into actual data

        // remove unwanted spaces
        elements.forEach(e => {
          if (e.data.id) e.data.id = e.data.id.trim();
          if (e.data.source) e.data.source = e.data.source.trim();
          if (e.data.target) e.data.target = e.data.target.trim();
        });

        // Create the graph
        const cy = cytoscape({
          container: document.getElementById('cy'),
          elements: elements, // load nodes and edges
          style: [
            { selector: 'node', style: { 'label': 'data(id)', 'background-color': '#0ba21b', 'border-width': 1, 'font-size': 9 } },
            { selector: 'edge', style: { 'width': 1.5, 'line-color': '#999', 'target-arrow-shape': 'vee' } }
          ],
          layout: { name: 'dagre', rankDir: 'TB', animate: false }
        });
      }
    }
  }, [departmentDetails]);

  // actual webpage code
  return (
    <div className="App">
      <Navbar expand="lg" bg="light" variant="light">
        <Container fluid>
          <Navbar.Brand href="#">CCSA</Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="ms-auto">
              <Button variant="outline-dark" type="submit" className="me-1">
                <Nav.Link href="/register">Add New User</Nav.Link>
              </Button>
              <Button variant="outline-dark" type="submit">
                <Nav.Link href="/logout">Logout</Nav.Link>
              </Button>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <div className="container-fluid mt-5">
        <div className="row"> {/* row one */}
          <div className="col-sm-3 col-md-3 col-lg-3 text-center"> {/* row one col one */}
            <DropdownButton
              id="school-dropdown"
              title={selectedUniversity}
              onSelect={(eventKey) => setSelectedUniversity(eventKey)}
              variant="outline-dark"
            >
              <Dropdown.Item eventKey="Kent State University">Kent State University</Dropdown.Item>
            </DropdownButton>
          </div>

          <div className="col-sm-3 col-md-3 col-lg-3 text-center"> {/* row one col two */}
            <DropdownButton
              id="year-dropdown"
              title={selectedYear}
              onSelect={(eventKey) => setSelectedYear(eventKey)}
              variant="outline-dark"
            >
              {years.map((year) => (
                <Dropdown.Item key={year} eventKey={year}>
                  {year}
                </Dropdown.Item>
              ))}
            </DropdownButton>
          </div>

          <div className="col-sm-3 col-md-3 col-lg-3 text-center"> {/* row one col three */}
            <DropdownButton
              id="department-dropdown"
              title={selectedDepartment}
              onSelect={(eventKey) => setSelectedDepartment(eventKey)}
              variant="outline-dark"
            >
              {departments.map((dept) => (
                <Dropdown.Item key={dept} eventKey={dept}>
                  {dept}
                </Dropdown.Item>
              ))}
            </DropdownButton>
          </div>

          <div className="col-sm-3 col-md-3 col-lg-3 text-center"> {/* row one col four */}
            <Button variant="outline-success" href="/ccsa-data.zip">
              Download Data
            </Button>
          </div>
        </div>

        <div className="row mt-2"> {/* row two */}
          {departmentDetails ? (
            <>
              <div className="col-sm-12 col-md-12 col-lg-12 d-flex justify-content-center align-items-center"> {/* row two col one */}
                {/* cytoscape dagre graph here */}
                <div id='cy' style={{ width: '100%', height: '50vh' }}></div>
              </div>

              <div className="col-sm-12 col-md-12 col-lg-12"> {/* row three col one */}
                <h3><strong>Selected Department: </strong>{departmentDetails.dept_name} {departmentDetails.year}</h3>
                <Accordion defaultActiveKey="0">
                  <Accordion.Item eventKey="0">
                    <Accordion.Header>Keywords in Course Descriptions</Accordion.Header>
                    <Accordion.Body>
                      {departmentDetails?.keywords ? (
                        <ul>
                          {departmentDetails.keywords.split(',').map((keyword, index) => (
                            <li key={index}>{keyword.trim()}</li>
                          ))}
                        </ul>
                      ) : (
                        <p>No keyword statistics available.</p>
                      )}
                    </Accordion.Body>
                  </Accordion.Item>
                  <Accordion.Item eventKey="1">
                    <Accordion.Header>Similar Departments</Accordion.Header>
                    <Accordion.Body>
                      <ul>

                      </ul>
                      {departmentDetails?.similar_depts ? (
                        <ul>
                          {departmentDetails.similar_depts.split(',').map((course, index) => (
                            <li key={index}>{course.trim()}</li>
                          ))}
                        </ul>
                      ) : (
                        <p>No similar department statistics available.</p>
                      )}
                    </Accordion.Body>
                  </Accordion.Item>
                  <Accordion.Item eventKey="2">
                    <Accordion.Header>Graph Cohesion Metrics</Accordion.Header>
                    <Accordion.Body>
                      {departmentDetails?.max_indegrees ? (
                        <p><strong>Max in-degree: </strong>{departmentDetails.max_indegrees}</p>
                      ) : (
                        <p><strong>Max in-degree: </strong> No max in-degree statistics available.</p>
                      )}

                      {departmentDetails?.max_outdegrees ? (
                        <p><strong>Max out-degree: </strong>{departmentDetails.max_outdegrees}</p>
                      ) : (
                        <p><strong>Max out-degree: </strong> No max out-degree statistics available.</p>
                      )}

                      {departmentDetails?.density ? (
                        <p><strong>Density: </strong>{departmentDetails.density}</p>
                      ) : (
                        <p><strong>Density: </strong> No density statistics available.</p>
                      )}
                    </Accordion.Body>
                  </Accordion.Item>
                </Accordion>
              </div>
            </>
          ) : (
            <h2><br></br>Select University, Year and Department</h2>
          )}
        </div>
      </div>
    </div>
  );
}

export default Home;
