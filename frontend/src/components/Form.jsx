import { useState } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import "../styles/Form.css";
import LoadingIndicator from "./LoadingIndicator";
import "bootstrap/dist/css/bootstrap.min.css";
import { Button } from "react-bootstrap";

function Form({ route, method }) {
    // useState is used for variables so that data persists between renders
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [badLoginAttempts, setBadLoginAttempts] = useState(0); // for tracking failed logins to implement timeout
    const [isBlocked, setIsBlocked] = useState(false);
    const navigate = useNavigate();

    const name = method === "login" ? "Login" : "Register";

    // handles submission of form
    const handleSubmit = async (e) => {
        e.preventDefault();

        // alerts user that their sign in is blocked
        if (isBlocked) {
            alert("Too many failed attempts. Please wait 30 seconds before trying again.");
            return;
        }

        setLoading(true);

        // try login
        try {
            const res = await api.post(route, { username, password });
            if (method === "login") {
                localStorage.setItem(ACCESS_TOKEN, res.data.access);
                localStorage.setItem(REFRESH_TOKEN, res.data.refresh);
                navigate("/");
            } else {
                navigate("/login");
            }
            setBadLoginAttempts(0); // reset bad attempts if successful
        } catch (error) {
            setBadLoginAttempts((prev) => prev + 1); // increments bad logins, if >= 5 user is placed in timeout
            
            if (badLoginAttempts + 1 >= 5) {
                alert("Too many failed login attempts. Please wait 30 seconds and try again.")
                setIsBlocked(true);
                setTimeout(() => {
                    setIsBlocked(false);
                }, 30000);
            } else {
                alert("Invalid Username or Password. Please try again."); // invalid username or pw (not >= 5 attempts)
            }
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
                disabled={isBlocked}
            />
            <input
                className="form-input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                disabled={isBlocked}
            />
            {loading && <LoadingIndicator />}
            <Button variant="outline-dark" type="submit" disabled={isBlocked}>
                {isBlocked ? "Blocked (Wait 30s)" : name}
            </Button>
        </form>
    );
}

export default Form;
