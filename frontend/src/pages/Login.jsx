import Form from "../components/Form"
import "../styles/Styles.css"

function Login() {

    return (
        <div>
            <h1>Course Catalog Statistical Analysis</h1>
            <Form route="/api/token/" method="login" />
            <div className="footer">
                <p>Disclaimer: All data was derived from publicly available Kent State University Catalog archives. We are not held liable for any conclusions drawn from discrepancies.</p>
            </div>
        </div>
    );
}

export default Login