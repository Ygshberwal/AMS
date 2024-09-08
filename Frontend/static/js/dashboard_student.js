document.addEventListener("DOMContentLoaded", () => {
    populateAttendanceView();
    handleClassSchedule();
  });
  
  function populateAttendanceView() {
    const tbody = document.getElementById("attendanceViewBody");
    tbody.innerHTML = '';
  
    for (let i = 1; i <= 45; i++) {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${i}</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
      `;
      tbody.appendChild(row);
    }
  }
  
  function handleAttendanceView() {
    document.getElementById('attendanceView').style.display = 'block';
    document.getElementById('classSchedule').style.display = 'none';
    document.getElementById('attendanceRequest').style.display = 'none';
    document.getElementById('leaveRequest').style.display = 'none';
  }
  
  function handleClassSchedule() {
    document.getElementById('attendanceView').style.display = 'none';
    document.getElementById('classSchedule').style.display = 'block';
    document.getElementById('attendanceRequest').style.display = 'none';
    document.getElementById('leaveRequest').style.display = 'none';
  }
  
  function handleAttendanceRequest() {
    document.getElementById('attendanceView').style.display = 'none';
    document.getElementById('classSchedule').style.display = 'none';
    document.getElementById('attendanceRequest').style.display = 'block';
    document.getElementById('leaveRequest').style.display = 'none';
  }
  
  function handleLeaveRequest() {
    document.getElementById('attendanceView').style.display = 'none';
    document.getElementById('classSchedule').style.display = 'none';
    document.getElementById('attendanceRequest').style.display = 'none';
    document.getElementById('leaveRequest').style.display = 'block';
  }
  