const table = document.querySelector('table');
const headerCells = table.querySelectorAll('th');
const rows = Array.from(table.querySelectorAll('tr')).slice(1);

function sortTable(columnIndex, ascending) {
  rows.sort((a, b) => {
    const aValue = a.querySelectorAll('td')[columnIndex].textContent;
    const bValue = b.querySelectorAll('td')[columnIndex].textContent;

    if (columnIndex === 0) {
      const aDate = new Date(aValue);
      const bDate = new Date(bValue);
      return ascending ? aDate - bDate : bDate - aDate;
    } else {
      const aNumber = parseInt(aValue.replace(/,/g, ''));
      const bNumber = parseInt(bValue.replace(/,/g, ''));
      return ascending ? aNumber - bNumber : bNumber - aNumber;
    }
  });

  // Remove existing rows from the table
  const tbody = table.querySelector('tbody');
  while (tbody.firstChild) {
    tbody.removeChild(tbody.firstChild);
  }

  // Add the sorted rows to the table
  rows.forEach(row => tbody.appendChild(row));
}

headerCells.forEach((header, index) => {
  header.addEventListener('click', () => {
    // Determine sort order based on current header class
    const sortOrder = header.classList.contains('ascending') ? 'descending' : 'ascending';
    const ascending = sortOrder === 'ascending';

    // Remove existing sort classes from header cells
    headerCells.forEach(header => header.classList.remove('ascending', 'descending'));

    // Add new sort class to the clicked header cell
    header.classList.add(sortOrder);

    sortTable(index, ascending);
  });
});
