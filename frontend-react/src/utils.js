export const currency = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

export function todayInput() {
  return new Date().toISOString().slice(0, 10);
}

export function currentMonthInput() {
  return todayInput().slice(0, 7);
}

export function isValidMonthInput(month) {
  return /^\d{4}-\d{2}$/.test(month || "");
}

export function monthLabel(month) {
  if (!isValidMonthInput(month)) return "";
  const [year, value] = month.split("-");
  return `${value}/${year}`;
}

export function weekLabel(dateText) {
  const [year, month, day] = (dateText || todayInput()).split("-").map(Number);
  const date = new Date(year, month - 1, day);
  const firstDay = new Date(year, month - 1, 1);
  const daysUntilSunday = 6 - firstDay.getDay();
  const firstWeekEnd = new Date(year, month - 1, 1 + daysUntilSunday);

  let weekNumber = 1;
  if (date > firstWeekEnd) {
    const millisecondsPerDay = 24 * 60 * 60 * 1000;
    const remainingDays = Math.floor((date - firstWeekEnd) / millisecondsPerDay);
    weekNumber = 1 + Math.floor((remainingDays - 1) / 7) + 1;
  }

  return `Semana ${weekNumber} - ${monthLabel((dateText || todayInput()).slice(0, 7))}`;
}

export function belongsToMonth(entry, month) {
  if (!isValidMonthInput(month)) return false;
  const label = monthLabel(month);
  if (entry.data_lancamento && entry.data_lancamento.startsWith(month)) return true;
  return String(entry.semana || "").includes(label);
}

export function employeeLabel(employee) {
  return `${employee.nome} - ${employee.cargo} - ${employee.turno || "Não informado"} (ID ${employee.id})`;
}

export function errorMessage(error) {
  try {
    const parsed = JSON.parse(error.message);
    return parsed.detail || error.message;
  } catch {
    return error.message;
  }
}
