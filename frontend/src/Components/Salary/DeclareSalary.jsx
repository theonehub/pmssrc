import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { getToken } from '../../utils/auth';
import PageLayout from '../../layout/PageLayout'; // Adjust path if needed

function DeclareSalary() {
  const [components, setComponents] = useState([]);
  const [declarations, setDeclarations] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [alert, setAlert] = useState({ type: '', message: '', show: false });

  const showAlert = (type, message) => {
    setAlert({ type, message, show: true });
    setTimeout(() => setAlert({ type: '', message: '', show: false }), 3000);
  };

  const fetchComponents = async () => {
    try {
      const res = await axios.get('http://localhost:8000/employee/salary-components', {
        headers: { Authorization: `Bearer ${getToken()}` },
      });

      const fetchedComponents = res.data;
      setComponents(fetchedComponents);

      const prefill = {};
      fetchedComponents.forEach((comp) => {
        if (comp.declared_amount) {
          prefill[comp.component_id] = comp.declared_amount;
        }
      });
      setDeclarations(prefill);
    } catch (err) {
      console.error('Error fetching components', err);
      showAlert('danger', 'Failed to fetch salary components');
    }
  };

  useEffect(() => {
    fetchComponents();
  }, []);

  const handleChange = (componentId, value) => {
    setDeclarations((prev) => ({
      ...prev,
      [componentId]: value,
    }));
  };

  const handleSubmit = async (component) => {
    const declaredAmount = parseFloat(declarations[component.component_id]);
    const { min_amount, max_amount, is_editable } = component;

    if (!is_editable) {
      showAlert('warning', 'You are not allowed to declare for this component');
      return;
    }

    if (isNaN(declaredAmount) || declaredAmount < min_amount || declaredAmount > max_amount) {
      showAlert('danger', `Amount must be between ₹${min_amount} and ₹${max_amount}`);
      return;
    }

    try {
      setSubmitting(true);
      await axios.post(
        'http://localhost:8000/employee/declare',
        {
          component_id: component.component_id,
          declared_amount: declaredAmount,
        },
        {
          headers: { Authorization: `Bearer ${getToken()}` },
        }
      );
      showAlert('success', 'Declaration submitted successfully!');
    } catch (err) {
      console.error('Error submitting declaration', err);
      showAlert('danger', 'Failed to submit declaration');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <PageLayout>
      <div className="container mt-4">
        <h3 className="mb-3">🧾 Declare Your Salary Components</h3>

        {alert.show && (
          <div className={`alert alert-${alert.type} alert-dismissible fade show`} role="alert">
            {alert.message}
            <button type="button" className="btn-close" onClick={() => setAlert({ ...alert, show: false })}></button>
          </div>
        )}

        {components.length === 0 ? (
          <p>No salary components assigned.</p>
        ) : (
          <table className="table table-bordered">
            <thead>
              <tr>
                <th>Component</th>
                <th>Min Amount (₹)</th>
                <th>Max Amount (₹)</th>
                <th>Already Declared (₹)</th>
                <th>Your Declaration (₹)</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {components.map((comp, idx) => (
                <tr key={idx}>
                  <td>{comp.component_name}</td>
                  <td>{comp.min_amount}</td>
                  <td>{comp.max_amount}</td>
                  <td>
                    {comp.declared_amount !== undefined ? (
                      <span className="text-success fw-semibold">{comp.declared_amount}</span>
                    ) : (
                      <span className="text-muted">—</span>
                    )}
                  </td>
                  <td>
                    {comp.is_editable ? (
                      <input
                        type="number"
                        className="form-control"
                        value={declarations[comp.component_id] || ''}
                        onChange={(e) => handleChange(comp.component_id, e.target.value)}
                      />
                    ) : comp.declared_amount ? (
                      <span>{comp.declared_amount}</span>
                    ) : (
                      <span className="text-muted">Not editable</span>
                    )}
                  </td>
                  <td>
                    {comp.is_editable && (
                      <button
                        className="btn btn-sm btn-primary"
                        onClick={() => handleSubmit(comp)}
                        disabled={submitting}
                      >
                        Submit
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </PageLayout>
  );
}

export default DeclareSalary;