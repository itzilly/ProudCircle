function checkDate() {
  console.log("checkDate run")
  let startDate = new Date(document.getElementById("start_date").value);
  let endDate = new Date(document.getElementById("end_date").value);
  let today = new Date();

  if (startDate > endDate) {
    alert("Start date must be before end date");
  } else if (startDate > today || endDate > today) {
    alert("Dates must be today or in the past");
  }
}
