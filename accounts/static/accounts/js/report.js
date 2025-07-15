document.addEventListener("DOMContentLoaded", function() {
  const dataElem = document.getElementById('income-expenses-data');
  if (!dataElem) return;
  const chartData = JSON.parse(dataElem.textContent);

  const ctx = document.getElementById('incomeVsExpensesChart').getContext('2d');
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Income', 'Expenses'],
      datasets: [{
        label: 'Amount',
        data: [chartData.income, chartData.expenses],
        backgroundColor: [
          'rgba(54, 162, 235, 0.7)',
          'rgba(255, 99, 132, 0.7)'
        ],
        borderColor: [
          'rgba(54, 162, 235, 1)',
          'rgba(255, 99, 132, 1)'
        ],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
});