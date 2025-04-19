// src/layout/PageLayout.js
import React from 'react';
import Sidebar from './Sidebar';
import Topbar from './Topbar';

const PageLayout = ({ title, children }) => {
  return (
    <div style={{ height: '100vh', overflow: 'hidden' }}>
      {/* Topbar spans full width */}
      <Topbar title={title} />

      {/* Content area: Sidebar + Main content */}
      <div className="d-flex" style={{ height: 'calc(100% - 56px)' }}>
        <Sidebar />
        <div className="flex-grow-1 p-4 bg-light overflow-auto">{children}</div>
      </div>
    </div>
  );
};

export default PageLayout;
