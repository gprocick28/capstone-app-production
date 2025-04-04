import { useState, useEffect } from "react"
import api from "../api"
import { useNavigate } from "react-router-dom"
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants"
import "../styles/Form.css"
import LoadingIndicator from "./LoadingIndicator"
import 'bootstrap/dist/css/bootstrap.min.css';
import { Button } from 'react-bootstrap';
import Nav from 'react-bootstrap/Nav';

function RegisterForm({ route, method }) {
    // useState is used for variables so that data persists between renders
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [isStaff, setIsStaff] = useState(false);
    const [loading, setLoading] = useState(false);
    const [userIsStaff, setUserIsStaff] = useState(false);
    const navigate = useNavigate();

    const name = method === "login" ? "Login" : "Register";

    // get user info from the server
    useEffect(() => {
        const fetchUserInfo = async () => {
            try {
                const res = await api.get("/api/user-info/"); 
                setUserIsStaff(res.data.is_staff);
            } catch (error) {
                console.error("Error fetching user info:", error);
            }
        };

        fetchUserInfo();
    }, []);

    // handles submission of form
    const handleSubmit = async (e) => {
        setLoading(true);
        e.preventDefault();

        // adjusts payload for registering new users - this form was adapted from the regular login form 'Form.jsx'
        const payload = { username, password };
        if (method === "register") {
            payload.is_staff = isStaff;
        }

        // tries to register - this form was adapted from the regular login form 'Form.jsx'
        try {
            const res = await api.post(route, payload);
            alert('User Created Successfully');
            if (method === "login") {
                console.log("Login successful:", res.data);
                localStorage.setItem("ACCESS_TOKEN", res.data.access);
                localStorage.setItem("REFRESH_TOKEN", res.data.refresh);
                navigate("/");
            } else {
                localStorage.setItem("ACCESS_TOKEN", res.data.access);
                localStorage.setItem("REFRESH_TOKEN", res.data.refresh);
                navigate("/register");
            }
        } catch (error) {
            console.error("Error:", error.response?.data || error.message);
            alert("Cannot register user. Username/Password is blank or Username is already in use. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="form-container">
            <h1>{name}</h1>
            <input
                className="form-input"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Username"
            />
            <input
                className="form-input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
            />
            
            {method === "register" && userIsStaff && (  // only show the staff checkbox if the user is a staff member
                <div className="form-checkbox">
                    <input
                        type="checkbox"
                        id="staff"
                        checked={isStaff}
                        onChange={(e) => setIsStaff(e.target.checked)}
                    />
                    <label htmlFor="staff">Register as Staff</label>
                </div>
            )}

            {loading && <LoadingIndicator />}
            
            {/* enable register button if the user is logged in as staff */}
            <Button variant="outline-dark" type="submit" disabled={!userIsStaff}>
                {name}
            </Button>

            <br></br>

            {/* return to catalog button */}
            <Button variant="outline-danger" type="button" onClick={() => navigate("/")}>
                <Nav.Link href="/">Return to Catalog</Nav.Link>
            </Button>

            {/* show message if the user is not logged in as a staff member */}
            {!userIsStaff && (
                <div className="error-message">
                    <br />
                    <p className="non-staff-message">Currently logged in as: USER</p>
                    <p className="non-staff-message">Must be logged in as ADMIN to register new users.</p>
                </div>
            )}
        </form>
    );
}

export default RegisterForm;
