import React, { useState, useEffect } from "react";
import axios from "axios";
import { getToken } from "../../utils/auth";
import PageLayout from "../../layout/PageLayout";

function SalaryComponents() {
  const [components, setComponents] = useState([]);
  const [newComponent, setNewComponent] = useState({
    name: "",
    type: "addition",
  });
  const [editingComponent, setEditingComponent] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [componentsPerPage] = useState(10);
  const [formErrors, setFormErrors] = useState({});

  const validateForm = () => {
    let errors = {};
    let isValid = true;

    if (!newComponent.name.trim()) {
      errors.name = "Name is required";
      isValid = false;
    }

    setFormErrors(errors);
    return isValid;
  };

  const validateEditForm = () => {
    let errors = {};
    let isValid = true;

    if (!editingComponent.name.trim()) {
      errors.name = "Name is required";
      isValid = false;
    }

    setFormErrors(errors);
    return isValid;
  };

  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
    setCurrentPage(1); // Reset to first page when search query changes
  };

  const filteredComponents = components.filter(
    (component) =>
      component.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      component.type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const indexOfLastComponent = currentPage * componentsPerPage;
  const indexOfFirstComponent = indexOfLastComponent - componentsPerPage;
  const currentComponents = filteredComponents.slice(
    indexOfFirstComponent,
    indexOfLastComponent
  );

  const paginate = (pageNumber) => setCurrentPage(pageNumber);
  const pageNumbers = [];
  for (let i = 1; i <= Math.ceil(filteredComponents.length / componentsPerPage); i++) {
    pageNumbers.push(i);
  }

  useEffect(() => {
    fetchComponents();
  }, []);

  const fetchComponents = async () => {
    try {
      const response = await axios.get(
        "http://localhost:8000/salary-components",
        {
          headers: { Authorization: `Bearer ${getToken()}` },
        }
      );
      setComponents(response.data);
    } catch (error) {
      console.error("Error fetching salary components:", error);
    }
  };

  const handleInputChange = (e) => {  
    setNewComponent({ ...newComponent, [e.target.name]: e.target.value });
  };

  const addComponent = async () => {
    try {
      await axios.post('http://localhost:8000/salary-components', newComponent, {
        headers: { Authorization: `Bearer ${getToken()}` },
      })
      if (validateForm()) {
       
        setNewComponent({ name: '', type: 'addition' });
        setShowAddModal(false);
      fetchComponents();
      }
    } catch (error) {
      console.error('Error adding salary component:', error);
    }
  };

  const startEditing = (component) => {
    setShowEditModal(true)
    setEditingComponent(component);
  };

  const handleEditInputChange = (e) => {  
    setEditingComponent({ ...editingComponent, [e.target.name]: e.target.value });
  };

  const updateComponent = async () => {
    try {
      await axios.put(`http://localhost:8000/salary-components/${editingComponent.id}`, editingComponent, {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      setEditingComponent(null);
      setShowEditModal(false);
      fetchComponents();
    } catch (error) {
      console.error('Error updating salary component:', error);
    }
  };

  const deleteComponent = async (id) => {
    if (window.confirm("Are you sure you want to delete this component?")) {
      try {
        await axios.delete(`http://localhost:8000/salary-components/${id}`, {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
        fetchComponents();
      } catch (error) {
        console.error('Error deleting salary component:', error);
      }
    }
  };

  return (
    <PageLayout>
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h3>Salary Components</h3>
          <button
            className="btn btn-primary"
            onClick={() => setShowAddModal(true)}
          >
            Add New Component
          </button>
        </div>
        <div className="mb-3">
          <input
            type="text"
            className="form-control"
            placeholder="Search by name or type"
            value={searchQuery}
            onChange={handleSearchChange}
          />
        </div>
        {/* Modal for Add new component */}
        {/* Add Component Modal */}
        <div className="modal-backdrop fade show" style={{display: showAddModal ? 'block' : 'none'}}></div>
        <div className="modal fade show" style={{display: showAddModal ? 'block' : 'none'}}>
     
      {/* Add Component Modal */}
      {showAddModal && (
        <div className="modal fade show" style={{ display: 'block' }} tabIndex="-1">
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Add New Component</h5>
                <button type="button" className="btn-close" onClick={() => setShowAddModal(false)}></button>
              </div>
              <div className="modal-body">  
                <div className="mb-3">
                  <label htmlFor="componentName" className="form-label">Name</label>
                  <input
                    type="text"
                    className="form-control"
                    id="componentName"
                    name="name"
                    value={newComponent.name}
                    onChange={handleInputChange}
                  />
                   {formErrors.name && <div className="text-danger">{formErrors.name}</div>}
                </div>
                <div className="mb-3">
                  <label htmlFor="componentType" className="form-label">Type</label>
                  <select
                    className="form-select"
                    id="componentType"
                    name="type"
                    value={newComponent.type}
                    onChange={handleInputChange}
                  >
                    <option value="addition">Addition</option>
                    <option value="deduction">Deduction</option>
                  </select>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowAddModal(false)}>
                  Cancel
                </button>
                <button type="button" className="btn btn-primary" onClick={addComponent}>
                  Add Component
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="table-responsive">
        {/* Edit Component Modal */}
        {/* Edit component modal */}
        <div className="modal-backdrop fade show" style={{display: showEditModal ? 'block' : 'none'}}></div>
        <div className="modal fade show" style={{display: showEditModal ? 'block' : 'none'}}>
        {showEditModal && (
          <div
            className="modal fade show"
            style={{ display: "block" }}
            tabIndex="-1"
          >
            <div className="modal-dialog">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">Edit Component</h5>
                  <button
                    type="button"
                    className="btn-close"
                    onClick={() => {setShowEditModal(false)
                    setEditingComponent(null)}}
                  ></button>
                </div>
                <div className="modal-body">
                  <div className="mb-3">
                    <label htmlFor="editComponentName" className="form-label">
                      Name
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      id="editComponentName"
                      name="name"
                      value={editingComponent?.name || ""}
                      onChange={handleEditInputChange}
                    />
                    {formErrors.name && <div className="text-danger">{formErrors.name}</div>}
                  </div>
                  <div className="mb-3">
                    <label htmlFor="editComponentType" className="form-label">
                      Type
                    </label>
                    <select
                      className="form-select"
                      id="editComponentType"
                      name="type"
                      value={editingComponent?.type || ""}
                      onChange={handleEditInputChange}
                    >
                      <option value="addition">Addition</option>
                      <option value="deduction">Deduction</option>
                    </select>
                  </div>
                </div>
                <div className="modal-footer">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => {setShowEditModal(false)
                    setEditingComponent(null)}}
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    className="btn btn-primary"
                    onClick={updateComponent}
                  >
                    Update Component
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
         </div>
         {/* Edit component modal end */}
        {/* Table to display component */}
        <table className="table table-striped table-bordered">   
         <thead className="thead-dark">

          {currentComponents.length === 0 && (
           <p>No components found.</p>
          )}
          <thead className="thead-dark">
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>        
                    component.name
                  )}
                </td>
                <td>
                  {editingComponent && editingComponent.id === component.id ? (
                    <select
                      className="form-select"
                      name="type"
                      value={editingComponent.type}
                      onChange={handleEditInputChange}
                    >
                      <option value="addition">Addition</option>
                      <option value="deduction">Deduction</option>
                    </select>
                  ) : (
                    component.type
                  )}
                </td>
          
                  <>
                    <button
                      className="btn btn-sm btn-warning me-2"
                      onClick={() => startEditing(component)}
                    >
                      Edit
                    </button>
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => deleteComponent(component.id)}
                    >
                      Delete
                    </button>
                  </>
                
              </tr>
            ))}            
          </tbody>
        </table>
          </tbody>
         {/* Table to display component end */}
      {/* Pagination */}
      <nav>
        <ul className="pagination">
          {pageNumbers.map((number) => (
            <li
              key={number}
              className={
                "page-item" + (currentPage === number ? " active" : "")
              }
            >
              <button
                onClick={() => paginate(number)}
                className="page-link"
              >
                {number}
              </button>
            </li>
          ))}
        </ul>
      </nav>
      {/* Pagination End*/}
      </div>
    </PageLayout>
  );
}

export default SalaryComponents;