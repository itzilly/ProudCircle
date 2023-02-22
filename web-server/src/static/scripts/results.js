// const table = document.querySelector('table');
// const rows = Array.from(table.querySelectorAll('tr')).slice(1);
//
// function sortTable(columnIndex, ascending) {
//   rows.sort((a, b) => {
//     const aValue = a.querySelectorAll('td')[columnIndex].textContent;
//     const bValue = b.querySelectorAll('td')[columnIndex].textContent;
//
//     if (columnIndex === 0) {
//       const aDate = new Date(aValue);
//       const bDate = new Date(bValue);
//       return ascending ? aDate - bDate : bDate - aDate;
//     } else {
//       const aNumber = parseInt(aValue.replace(/,/g, ''));
//       const bNumber = parseInt(bValue.replace(/,/g, ''));
//       return ascending ? aNumber - bNumber : bNumber - aNumber;
//     }
//   });
//
//   // Remove existing rows from the table
//   const tbody = table.querySelector('tbody');
//   while (tbody.firstChild) {
//     tbody.removeChild(tbody.firstChild);
//   }
//
//   // Add the sorted rows to the table
//   rows.forEach(row => tbody.appendChild(row));
// }
//
// document.getElementById('sort-date-asc').addEventListener('click', () => {
//   sortTable(0, true);
// });
//
// document.getElementById('sort-date-desc').addEventListener('click', () => {
//   sortTable(0, false);
// });
//
// document.getElementById('sort-amount-asc').addEventListener('click', () => {
//   sortTable(1, true);
// });
//
// document.getElementById('sort-amount-desc').addEventListener('click', () => {
//   sortTable(1, false);
// });

// get the table and all its rows
const table = document.getElementById('results-table');
const rows = table.getElementsByTagName('tr');

// get the date and amount header cells
const dateHeader = document.getElementById('date-header');
const amountHeader = document.getElementById('amount-header');

// add click event listeners to the header cells
dateHeader.addEventListener('click', () => sortTable(0));
amountHeader.addEventListener('click', () => sortTable(1));

// sort the table by the specified column
function sortTable(columnIndex) {
  const rowsArray = Array.prototype.slice.call(rows, 1); // skip the header row
  rowsArray.sort((row1, row2) => {
    const cell1 = row1.getElementsByTagName('td')[columnIndex];
    const cell2 = row2.getElementsByTagName('td')[columnIndex];
    if (columnIndex === 0) { // sort by date
      const date1 = new Date(cell1.textContent);
      const date2 = new Date(cell2.textContent);
      return date1 - date2;
    } else { // sort by amount
      const amount1 = parseFloat(cell1.textContent.replace(/,/g, ''));
      const amount2 = parseFloat(cell2.textContent.replace(/,/g, ''));
      return amount1 - amount2;
    }
  });
  // remove existing table rows and append the sorted ones
  while (table.rows.length > 1) {
    table.deleteRow(1);
  }
  for (let i = 0; i < rowsArray.length; i++) {
    table.appendChild(rowsArray[i]);
  }
}
