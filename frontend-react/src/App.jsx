import {
  BarChart3,
  CalendarCheck,
  ChevronDown,
  FileSpreadsheet,
  History,
  LayoutDashboard,
  ListChecks,
  Plus,
  RefreshCw,
  Save,
  Search,
  Trash2,
  Users,
  Pencil,
  BookOpen,
  LogOut,
  Moon,
  SlidersHorizontal,
  Sun
} from "lucide-react";
import { Fragment, useEffect, useMemo, useState } from "react";
import { api, downloadUrl } from "./api";
import {
  belongsToMonth,
  currency,
  currentMonthInput,
  employeeLabel,
  errorMessage,
  todayInput,
  weekLabel,
} from "./utils";

const tabs = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "funcionarios", label: "Funcionários", icon: Users },
  { id: "lancamentos", label: "Lançamentos", icon: ListChecks },
  { id: "historico-lancamentos", label: "Listar Lançamentos", icon: History },
  { id: "frequencias", label: "Frequência", icon: CalendarCheck },
  { id: "fechamento", label: "Fechamento", icon: FileSpreadsheet },
  { id: "regras", label: "Regras", icon: BookOpen},
];

const initialEmployee = {
  nome: "",
  cargo: "",
  ativo: true,
  tipo_entrega: "Não se aplica",
  turno: "Manhã",
};

const USERS = {
  admin: "8599256",
  iann: "1234",
  valesca: "Rhcem123@",
  paulo: "Cempaulo123@",
  romario: "Cemromario123@",
};

function readLoggedUser() {
  const params = new URLSearchParams(window.location.search);
  const token = params.get("auth") || localStorage.getItem("bonificacao_auth");
  const storedUser = localStorage.getItem("bonificacao_user");

  if (storedUser) return storedUser;
  if (!token) return "";

  try {
    const payload = token.split(".")[0];
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    const padded = normalized.padEnd(normalized.length + ((4 - (normalized.length % 4)) % 4), "=");
    return JSON.parse(atob(padded)).usuario || "";
  } catch {
    return "";
  }
}

function useApiData() {
  const [employees, setEmployees] = useState([]);
  const [entries, setEntries] = useState([]);
  const [frequencies, setFrequencies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [funcionarios, lancamentos, frequencias] = await Promise.all([
        api.get("/funcionarios"),
        api.get("/lancamentos-semanais"),
        api.get("/frequencias"),
      ]);
      setEmployees(funcionarios);
      setEntries(lancamentos);
      setFrequencies(frequencias);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return { employees, entries, frequencies, loading, error, load };
}

export function App() {
  const [activeTab, setActiveTab] = useState(() => localStorage.getItem("bonificacao_active_tab") || "dashboard");
  const [loggedUser, setLoggedUser] = useState(readLoggedUser);
  const [theme, setTheme] = useState(() => localStorage.getItem("bonificacao_theme") || "light");
  const data = useApiData();

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("bonificacao_theme", theme);
  }, [theme]);

  useEffect(() => {
    localStorage.setItem("bonificacao_active_tab", activeTab);
  }, [activeTab]);

  function handleLogout() {
    const params = new URLSearchParams(window.location.search);
    params.delete("auth");
    localStorage.removeItem("bonificacao_auth");
    localStorage.removeItem("bonificacao_user");
    window.history.replaceState(null, "", window.location.pathname);
    setLoggedUser("");
  }

  function handleLogin(user) {
    localStorage.setItem("bonificacao_user", user);
    setLoggedUser(user);
  }

  if (!loggedUser) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span>Bonificação</span>
          <strong>Performance</strong>
          {loggedUser && <small>Logado como {loggedUser}</small>}
        </div>

        <nav>
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                className={activeTab === tab.id ? "active" : ""}
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                type="button"
              >
                <Icon size={18} />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p>Sistema de bônus</p>
            <h1>{tabs.find((tab) => tab.id === activeTab)?.label}</h1>
          </div>
          <div className="topbar-actions">
            <button className="icon-button" onClick={data.load} title="Atualizar dados" type="button">
              <RefreshCw size={18} />
            </button>
            <button
              className="icon-button"
              onClick={() => setTheme((current) => (current === "dark" ? "light" : "dark"))}
              title={theme === "dark" ? "Usar tema claro" : "Usar tema escuro"}
              type="button"
            >
              {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <button className="icon-button" onClick={handleLogout} title="Sair" type="button">
              <LogOut size={18} />
            </button>
          </div>
        </header>

        {data.error && <div className="alert error">{data.error}</div>}
        {data.loading && <div className="alert">Carregando dados da API...</div>}

        {!data.loading && activeTab === "dashboard" && <Dashboard {...data} />}
        {!data.loading && activeTab === "funcionarios" && <Employees {...data} />}
        {!data.loading && activeTab === "lancamentos" && <Entries {...data} mode="form" />}
        {!data.loading && activeTab === "historico-lancamentos" && <Entries {...data} mode="history" />}
        {!data.loading && activeTab === "frequencias" && <Frequencies {...data} />}
        {!data.loading && activeTab === "fechamento" && <Closing {...data} />}
        {!data.loading && activeTab === "regras" && <Rules />}
      </main>
    </div>
  );
}

function LoginScreen({ onLogin }) {
  const [form, setForm] = useState({ usuario: "", senha: "" });
  const [error, setError] = useState("");

  function submitLogin(event) {
    event.preventDefault();
    const user = form.usuario.trim();

    if (USERS[user] !== form.senha) {
      setError("Usuário ou senha inválidos.");
      return;
    }

    setError("");
    onLogin(user);
  }

  return (
    <main className="login-screen">
      <form className="login-card" onSubmit={submitLogin}>
        <div className="login-mark">B</div>
        <span>Sistema de bônus</span>
        <h1>Entrar no painel</h1>
        <p>Use seu usuário e senha para acessar os lançamentos, frequência e fechamento.</p>

        {error && <div className="alert error">{error}</div>}

        <input
          autoComplete="username"
          autoFocus
          placeholder="Usuário"
          value={form.usuario}
          onChange={(event) => setForm({ ...form, usuario: event.target.value })}
          required
        />

        <input
          autoComplete="current-password"
          placeholder="Senha"
          type="password"
          value={form.senha}
          onChange={(event) => setForm({ ...form, senha: event.target.value })}
          required
        />

        <button className="primary" type="submit">
          Entrar
        </button>
      </form>
    </main>
  );
}

function Dashboard({ employees, entries }) {
  const [month, setMonth] = useState(currentMonthInput());
  const [closing, setClosing] = useState([]);
  const [error, setError] = useState("");
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [periodStart, setPeriodStart] = useState("");
  const [periodEnd, setPeriodEnd] = useState("");
  const [dateScope, setDateScope] = useState("Todos");
  const [weekFilter, setWeekFilter] = useState("Todos");

  useEffect(() => {
    api
      .get(`/fechamento/${month}`)
      .then(setClosing)
      .catch((err) => setError(errorMessage(err)));
  }, [month]);

  const monthEntries = entries.filter((entry) => belongsToMonth(entry, month));
  const weeks = [...new Set(monthEntries.map((entry) => entry.semana).filter(Boolean))].sort();
  const filteredEntries = entries.filter((entry) => {
    const entryDate = entry.data_lancamento || "";
    const entryMonth = entryDate.slice(0, 7);
    const entryYear = entryDate.slice(0, 4);
    const selectedYear = month.slice(0, 4);

    const matchesDateScope =
      dateScope === "Todos" ||
      (dateScope === "Ano" && entryYear === selectedYear) ||
      (dateScope === "Mês" && entryMonth === month) ||
      (dateScope === "Data" && (!periodStart || entryDate === periodStart));

    return (
      matchesDateScope &&
      (!periodStart || entryDate >= periodStart) &&
      (!periodEnd || entryDate <= periodEnd) &&
      (weekFilter === "Todos" || entry.semana === weekFilter)
    );
  });
  const hasAdvancedFilters = Boolean(periodStart || periodEnd || dateScope !== "Todos" || weekFilter !== "Todos");
  const dashboardEntries = hasAdvancedFilters ? filteredEntries : monthEntries;
  const filteredEmployeeIds = new Set(dashboardEntries.map((entry) => entry.funcionario_id));
  const rankingItems = hasAdvancedFilters
    ? closing.filter((item) => filteredEmployeeIds.has(item.funcionario_id))
    : closing;
  const activeEmployees = employees.filter((employee) => employee.ativo);
  const visibleActiveEmployees = hasAdvancedFilters
    ? activeEmployees.filter((employee) => filteredEmployeeIds.has(employee.id))
    : activeEmployees;
  const totalBonus = rankingItems.reduce((sum, item) => sum + Number(item.bonus_final || 0), 0);
  const blocked = rankingItems.filter((item) => !item.elegivel).length;
  const eligible = rankingItems.filter((item) => item.elegivel).length;
  const assiduity = rankingItems.reduce((sum, item) => sum + Number(item.assiduidade || 0), 0);

  function clearDashboardFilters() {
    setPeriodStart("");
    setPeriodEnd("");
    setDateScope("Todos");
    setWeekFilter("Todos");
  }

  return (
    <section className="view">
      <div className="dashboard-filters">
        <div className="toolbar">
          <label>
            Mês
            <input type="month" value={month} onChange={(event) => setMonth(event.target.value)} />
          </label>
        </div>

        <section className={`panel advanced-filter ${advancedOpen ? "open" : ""}`}>
          <button className="advanced-filter-toggle" onClick={() => setAdvancedOpen((current) => !current)} type="button">
            <span>
              <SlidersHorizontal size={18} />
              Filtro avançado
            </span>
            <ChevronDown size={18} />
          </button>

          {advancedOpen && (
            <div className="advanced-filter-body">
              <p>Selecione os filtros abaixo para melhorar a análise:</p>

              <div className="advanced-filter-grid">
                <fieldset>
                  <legend>Período</legend>
                  <input type="date" value={periodStart} onChange={(event) => setPeriodStart(event.target.value)} />
                  <input type="date" value={periodEnd} onChange={(event) => setPeriodEnd(event.target.value)} />
                </fieldset>

                <label>
                  Ano, Mês, Data
                  <select value={dateScope} onChange={(event) => setDateScope(event.target.value)}>
                    <option>Todos</option>
                    <option>Ano</option>
                    <option>Mês</option>
                    <option>Data</option>
                  </select>
                </label>

                <label>
                  Semana
                  <select value={weekFilter} onChange={(event) => setWeekFilter(event.target.value)}>
                    <option>Todos</option>
                    {weeks.map((week) => (
                      <option key={week}>{week}</option>
                    ))}
                  </select>
                </label>

                <button className="icon-button wide-button" onClick={clearDashboardFilters} type="button">
                  Limpar filtros
                </button>
              </div>
            </div>
          )}
        </section>
      </div>

      {error && <div className="alert error">{error}</div>}

      <div className="metrics">
        <Metric label="Funcionários ativos" value={visibleActiveEmployees.length} />
        <Metric label="Lançamentos no mês" value={dashboardEntries.length} />
        <Metric label="Total bônus" value={currency.format(totalBonus)} />
        <Metric label="Bloqueados" value={blocked} />
      </div>

      <div className="split">
        <section>
          <h2>Elegibilidade</h2>
          <div className="summary-line"><span>Elegíveis</span><strong>{eligible}</strong></div>
          <div className="summary-line"><span>Bloqueados</span><strong>{blocked}</strong></div>
          <div className="summary-line"><span>Assiduidade</span><strong>{currency.format(assiduity)}</strong></div>
        </section>
        <section>
          <h2>Ranking</h2>
          <div className="list">
            {[...rankingItems]
              .sort((a, b) => Number(b.bonus_final || 0) - Number(a.bonus_final || 0))
              .slice(0, 10)
              .map((item, index) => (
                <div className="row-card" key={item.funcionario_id}>
                  <strong>{index + 1}. {item.funcionario}</strong>
                  <span>{item.cargo}</span>
                  <b>{currency.format(Number(item.bonus_final || 0))}</b>
                </div>
              ))}
          </div>
        </section>
      </div>
    </section>
  );
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function Employees({ employees, load }) {
  const [form, setForm] = useState(initialEmployee);
  const [search, setSearch] = useState("");
  const [message, setMessage] = useState("");
  const [editing, setEditing] = useState(null);

  const filtered = employees.filter((employee) => {
    const text = `${employee.nome} ${employee.cargo} ${employee.turno} ${employee.tipo_entrega}`.toLowerCase();
    return text.includes(search.toLowerCase());
  });

  async function saveEmployee(event) {
    event.preventDefault();
    setMessage("");
    try {
      await api.post("/funcionarios", form);
      setForm(initialEmployee);
      await load();
      setMessage("Funcionário cadastrado.");
    } catch (err) {
      setMessage(errorMessage(err));
    }
  }

  async function removeEmployee(id) {
    if (!confirm("Excluir funcionário e seus lançamentos?")) return;
    await api.delete(`/funcionarios/${id}`);
    await load();
  }

  async function updateEmployee(event) {
    event.preventDefault();
    setMessage("");
    
    try {
    await api.put(`/funcionarios/${editing.id}`, {
      nome: editing.nome,
      cargo: editing.cargo,
      ativo: editing.ativo,
      tipo_entrega: editing.tipo_entrega,
      turno: editing.turno,
    });

    setEditing(null);
    await load(); 
    setMessage("Funcionário atualizado.");
  } catch (err) {
    setMessage(errorMessage(err))
  }
}
  return (
    <section className="view">
      <form className="panel form-grid" onSubmit={saveEmployee}>
        <h2>Cadastrar funcionário</h2>
        <input placeholder="Nome" value={form.nome} onChange={(event) => setForm({ ...form, nome: event.target.value })} required />
        <input placeholder="Cargo" value={form.cargo} onChange={(event) => setForm({ ...form, cargo: event.target.value })} required />
        <select value={form.tipo_entrega} onChange={(event) => setForm({ ...form, tipo_entrega: event.target.value })}>
          <option>Não se aplica</option>
          <option>Entrega</option>
        </select>
        <select value={form.turno} onChange={(event) => setForm({ ...form, turno: event.target.value })}>
          <option>Manhã</option>
          <option>Tarde</option>
          <option>Noite</option>
        </select>
        <label className="check">
          <input checked={form.ativo} type="checkbox" onChange={(event) => setForm({ ...form, ativo: event.target.checked })} />
          Ativo
        </label>
        <button className="primary" type="submit"><Plus size={17} /> Salvar</button>
      </form>

      {message && <div className="alert">{message}</div>}

      <div className="toolbar">
        <label className="search">
          <Search size={17} />
          <input placeholder="Pesquisar funcionário" value={search} onChange={(event) => setSearch(event.target.value)} />
        </label>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr><th>ID</th><th>Nome</th><th>Cargo</th><th>Turno</th><th>Entrega</th><th>Status</th><th></th></tr>
          </thead>
          <tbody>
            {filtered.map((employee) => (
              <Fragment key={employee.id}>
                <tr>
                  <td>{employee.id}</td>
                  <td>{employee.nome}</td>
                  <td>{employee.cargo}</td>
                  <td>{employee.turno}</td>
                  <td>{employee.tipo_entrega}</td>
                  <td><span className={employee.ativo ? "badge ok" : "badge muted"}>{employee.ativo ? "Ativo" : "Inativo"}</span></td>
                  <td>
                    <button
                      className="icon-button"
                      onClick={() => setEditing(employee)}
                      title="Editar funcionário"
                      type="button"
                    >
                      <Pencil size={16} />
                    </button>

                    <button 
                      className="icon-button danger" 
                      onClick={() => removeEmployee(employee.id)} 
                      title="Excluir funcionário" 
                      type="button"
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>

                {editing?.id === employee.id && (
                  <tr className="inline-edit-row">
                    <td colSpan="7">
                      <form className="inline-edit-form form-grid" onSubmit={updateEmployee}>
                        <h2>Editar funcionário</h2>

                        <input value={editing.nome} onChange={(event) => setEditing({ ...editing, nome: event.target.value })} required />
                        <input value={editing.cargo} onChange={(event) => setEditing({ ...editing, cargo: event.target.value })} required />

                        <select value={editing.tipo_entrega} onChange={(event) => setEditing({ ...editing, tipo_entrega: event.target.value})}>
                          <option>Não se aplica</option>
                          <option>Entrega</option>
                        </select>

                        <select value={editing.turno} onChange={(event) => setEditing({ ...editing, turno: event.target.value})}>
                          <option>Manhã</option>
                          <option>Tarde</option>
                          <option>Noite</option>
                        </select>

                        <label className="check">
                          <input checked={editing.ativo} type="checkbox" onChange={(event) => setEditing({ ...editing, ativo: event.target.checked})} />
                          Ativo
                        </label>

                        <button className="primary" type="submit">
                          <Save size={17} /> Salvar alterações
                        </button>

                        <button className="icon-button" onClick={() => setEditing(null)} type="button">
                          X
                        </button>
                      </form>
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function Entries({ employees, entries, load, mode = "all" }) {
  const [form, setForm] = useState({
    funcionario_id: "",
    tipo_lancamento: "semanal",
    data_lancamento: todayInput(),
    pedidos_separados: 0,
    pedidos_carregados: 0,
    toneladas: 0,
    entregas: 0,
    retornos: 0,
    nota: 3,
    penalidade: false,
    motivo_penalidade: "",
  });
  const [month, setMonth] = useState(currentMonthInput());
  const [dayFilter, setDayFilter] = useState("");
  const [nameFilter, setNameFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("Todos");
  const [turnFilter, setTurnFilter] = useState("Todos");
  const [minBonusFilter, setMinBonusFilter] = useState("");
  const [maxBonusFilter, setMaxBonusFilter] = useState("");
  const [message, setMessage] = useState("");
  const employeeMap = useMemo(() => Object.fromEntries(employees.map((employee) => [employee.id, employee])), [employees]);
  const [editingEntry, setEditingEntry] = useState(null);
  const [monthlyForm, setMonthlyForm] = useState({
    mes: currentMonthInput(),
    filtro_turno: "Manhã",
    tipo_funcionario: "Funcionário normal",
    pedidos_separados: 0,
    pedidos_carregados: 0,
    toneladas: 0,
    entregas: 0,
    retornos: 0,
    notas: {},
  });

  function normalizeText(value) {
    return String(value || "")
      .trim()
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
  }

  function appliesToMonthly(employee) {
    if (!employee.ativo) return false;
    if (normalizeText(employee.turno) !== normalizeText(monthlyForm.filtro_turno)) return false;

    const deliveryType = normalizeText(employee.tipo_entrega);
    const employeeType = normalizeText(monthlyForm.tipo_funcionario);

    if (employeeType === "funcionario normal") {
      return ["", "nao se aplica", "n?o se aplica"].includes(deliveryType);
    }

    if (employeeType === "entrega") {
      return ["entrega", "motorista", "ajudante", "ajudante de motorista"].includes(deliveryType);
    }

    return deliveryType === employeeType;
  }

  function isDeliveryEmployee(employee) {
    return ["entrega", "motorista", "ajudante", "ajudante de motorista"].includes(
      normalizeText(employee?.tipo_entrega),
    );
  }

  const monthlyEmployees = useMemo(
    () => employees.filter(appliesToMonthly),
    [employees, monthlyForm.filtro_turno, monthlyForm.tipo_funcionario],
  );
  const selectedEmployee = form.funcionario_id ? employeeMap[form.funcionario_id] : null;
  const selectedEmployeeTurn = normalizeText(selectedEmployee?.turno);
  const selectedEmployeeIsDelivery = isDeliveryEmployee(selectedEmployee);
  const editingEmployee = editingEntry ? employeeMap[editingEntry.funcionario_id] : null;
  const editingEmployeeTurn = normalizeText(editingEmployee?.turno);
  const editingEmployeeIsDelivery = isDeliveryEmployee(editingEmployee);
  const monthlyIsDelivery = normalizeText(monthlyForm.tipo_funcionario) === "entrega";
  const showForm = mode !== "history";
  const showHistory = mode !== "form";

  async function saveEntry(event) {
    event.preventDefault();
    const payload = {
      ...form,
      funcionario_id: Number(form.funcionario_id),
      semana: form.tipo_lancamento === "diario" ? weekLabel(form.data_lancamento) : weekLabel(form.data_lancamento),
      data_lancamento: form.data_lancamento,
      pedidos_separados: Number(form.pedidos_separados),
      pedidos_carregados: Number(form.pedidos_carregados),
      toneladas: selectedEmployeeIsDelivery ? 0 : Number(form.toneladas),
      entregas: Number(form.entregas || 0),
      retornos: Number(form.retornos || 0),
      nota: Number(form.nota),
      motivo_penalidade: form.penalidade ? form.motivo_penalidade : null,
    };
    setMessage("");
    try {
      const saved = await api.post("/lancamentos-semanais", payload);
      await load();
      setMessage(`Lançamento salvo. Bônus: ${currency.format(Number(saved.bonus_calculado || 0))}`);
    } catch (err) {
      setMessage(errorMessage(err));
    }
  }

  async function removeEntry(id) {
    if (!confirm("Excluir lançamento?")) return;
    await api.delete(`/lancamentos-semanais/${id}`);
    await load();
  }

  async function saveMonthlyEntries(event) {
    event.preventDefault();
    setMessage("");

    if (!monthlyEmployees.length) {
      setMessage("Nenhum funcionário ativo encontrado para os filtros do lançamento mensal.");
      return;
    }

    const notes = Object.fromEntries(
      monthlyEmployees.map((employee) => [
        employee.id,
        Number(monthlyForm.notas[employee.id] || 5),
      ]),
    );

    try {
      const saved = await api.post("/lancamentos-mensais", {
        mes: monthlyForm.mes,
        filtro_turno: monthlyForm.filtro_turno,
        tipo_funcionario: monthlyForm.tipo_funcionario,
        usuario_lancamento: null,
        pedidos_separados: Number(monthlyForm.pedidos_separados),
        pedidos_carregados: Number(monthlyForm.pedidos_carregados),
        toneladas: monthlyIsDelivery ? 0 : Number(monthlyForm.toneladas),
        entregas: Number(monthlyForm.entregas || 0),
        retornos: Number(monthlyForm.retornos || 0),
        notas: notes,
      });

      await load();
      setMessage(`Lançamento mensal salvo para ${saved.length} funcionário(s).`);
    } catch (err) {
      setMessage(errorMessage(err));
    }
  }

  const filteredEntries = entries.filter((entry) => {
    const employee = employeeMap[entry.funcionario_id] || {};
    const entryType = normalizeText(entry.tipo_lancamento || "semanal");
    const employeeTurn = normalizeText(employee.turno);
    const employeeName = normalizeText(employee.nome);
    const bonus = Number(entry.bonus_calculado || 0);
    const minBonus = minBonusFilter === "" ? null : Number(minBonusFilter);
    const maxBonus = maxBonusFilter === "" ? null : Number(maxBonusFilter);

    return (
      belongsToMonth(entry, month) &&
      (!dayFilter || entry.data_lancamento === dayFilter) &&
      (!nameFilter.trim() || employeeName.includes(normalizeText(nameFilter))) &&
      (typeFilter === "Todos" || entryType === normalizeText(typeFilter)) &&
      (turnFilter === "Todos" || employeeTurn === normalizeText(turnFilter)) &&
      (minBonus === null || bonus >= minBonus) &&
      (maxBonus === null || bonus <= maxBonus)
    );
  });

  function clearEntryFilters() {
    setMonth(currentMonthInput());
    setDayFilter("");
    setNameFilter("");
    setTypeFilter("Todos");
    setTurnFilter("Todos");
    setMinBonusFilter("");
    setMaxBonusFilter("");
  }

  async function updateEntry(event) {
    event.preventDefault();
    setMessage("");

    try {
      await api.put(`/lancamentos-semanais/${editingEntry.id}`, {
        semana: editingEntry.semana,
        data_lancamento: editingEntry.data_lancamento,
        pedidos_separados: Number(editingEntry.pedidos_separados),
        pedidos_carregados: Number(editingEntry.pedidos_carregados),
        toneladas: editingEmployeeIsDelivery ? 0 : Number(editingEntry.toneladas),
        entregas: Number(editingEntry.entregas || 0),
        retornos: Number(editingEntry.retornos || 0),
        nota: Number(editingEntry.nota),
        penalidade: Boolean(editingEntry.penalidade),
        motivo_penalidade: editingEntry.penalidade
        ? editingEntry.motivo_penalidade
        : null,
      });

      setEditingEntry(null);
      await load();
      setMessage("Lançamento atualizado.")
    } catch (err){
      setMessage(errorMessage(err));
    }
}

  function renderEntryEditForm() {
    if (!editingEntry) return null;

    return (
      <form className="inline-edit-form form-grid entries-form" onSubmit={updateEntry}>
        <h2>Editar lançamento</h2>

        <input value={editingEntry.semana} onChange={(event) => setEditingEntry({ ...editingEntry, semana: event.target.value })} required />
        <input type="date" value={editingEntry.data_lancamento || ""} onChange={(event) => setEditingEntry({ ...editingEntry, data_lancamento: event.target.value })} />

        {!editingEmployeeIsDelivery && editingEmployeeTurn === "manha" && (
          <input min="0" step="0.1" type="number" placeholder="Toneladas" value={editingEntry.toneladas} onChange={(event) => setEditingEntry({ ...editingEntry, pedidos_separados: 0, pedidos_carregados: 0, toneladas: event.target.value })} />
        )}

        {!editingEmployeeIsDelivery && editingEmployeeTurn === "tarde" && (
          <input min="0" type="number" placeholder="Pedidos separados" value={editingEntry.pedidos_separados} onChange={(event) => setEditingEntry({ ...editingEntry, pedidos_separados: event.target.value, pedidos_carregados: 0, toneladas: 0 })} />
        )}

        {!editingEmployeeIsDelivery && editingEmployeeTurn === "noite" && (
          <input min="0" type="number" placeholder="Pedidos carregados" value={editingEntry.pedidos_carregados} onChange={(event) => setEditingEntry({ ...editingEntry, pedidos_separados: 0, pedidos_carregados: event.target.value, toneladas: 0 })} />
        )}

        {editingEmployeeIsDelivery && (
          <>
            <input min="0" type="number" placeholder="Entregas" value={editingEntry.entregas || 0} onChange={(event) => setEditingEntry({ ...editingEntry, entregas: event.target.value })} />
            <input min="0" type="number" placeholder="Retornos" value={editingEntry.retornos || 0} onChange={(event) => setEditingEntry({ ...editingEntry, retornos: event.target.value })} />
          </>
        )}

        <select value={editingEntry.nota} onChange={(event) => setEditingEntry({ ...editingEntry, nota: event.target.value })}>
          {[1, 2, 3, 4, 5].map((note) => <option key={note}>{note}</option>)}
        </select>

        <label className="check">
          <input checked={editingEntry.penalidade} type="checkbox" onChange={(event) => setEditingEntry({ ...editingEntry, penalidade: event.target.checked })} />
          Penalidade
        </label>

        {editingEntry.penalidade && (
          <input placeholder="Motivo" value={editingEntry.motivo_penalidade || ""} onChange={(event) => setEditingEntry({ ...editingEntry, motivo_penalidade: event.target.value })} required />
        )}

        <button className="primary" type="submit"><Save size={17} /> Salvar alterações</button>
        <button className="icon-button" onClick={() => setEditingEntry(null)} type="button">X</button>
      </form>
    );
  }

  return (
    <section className="view">
      {showForm && (
        <>
          <div className="panel form-grid">
            <h2>Novo lançamento</h2>
            <select value={form.tipo_lancamento} onChange={(event) => setForm({ ...form, tipo_lancamento: event.target.value })}>
              <option value="semanal">Semanal</option>
              <option value="diario">Diário</option>
              <option value="mensal">Mensal</option>
            </select>
          </div>

          {form.tipo_lancamento !== "mensal" && (
            <form className="panel form-grid entries-form" onSubmit={saveEntry}>
          <h2>{form.tipo_lancamento === "diario" ? "Lançamento diário" : "Lançamento semanal"}</h2>
          <select
            value={form.funcionario_id}
            onChange={(event) =>
              setForm({
                ...form,
                funcionario_id: event.target.value,
                pedidos_separados: 0,
                pedidos_carregados: 0,
                toneladas: 0,
                entregas: 0,
                retornos: 0,
              })
            }
            required
          >
            <option value="">Funcionário</option>
            {employees.filter((employee) => employee.ativo).map((employee) => (
              <option key={employee.id} value={employee.id}>{employeeLabel(employee)}</option>
            ))}
          </select>
          <input type="date" value={form.data_lancamento} onChange={(event) => setForm({ ...form, data_lancamento: event.target.value })} />
          {!selectedEmployeeIsDelivery && selectedEmployeeTurn === "manha" && (
            <input
              min="0"
              step="0.1"
              type="number"
              placeholder="Toneladas"
              value={form.toneladas}
              onChange={(event) =>
                setForm({
                  ...form,
                  pedidos_separados: 0,
                  pedidos_carregados: 0,
                  toneladas: event.target.value,
                })
              }
            />
          )}
          {!selectedEmployeeIsDelivery && selectedEmployeeTurn === "tarde" && (
            <input
              min="0"
              type="number"
              placeholder="Pedidos separados"
              value={form.pedidos_separados}
              onChange={(event) =>
                setForm({
                  ...form,
                  pedidos_separados: event.target.value,
                  pedidos_carregados: 0,
                  toneladas: 0,
                })
              }
            />
          )}
          {!selectedEmployeeIsDelivery && selectedEmployeeTurn === "noite" && (
            <input
              min="0"
              type="number"
              placeholder="Pedidos carregados"
              value={form.pedidos_carregados}
              onChange={(event) =>
                setForm({
                  ...form,
                  pedidos_separados: 0,
                  pedidos_carregados: event.target.value,
                  toneladas: 0,
                })
              }
            />
          )}
          {selectedEmployeeIsDelivery && (
            <>
              <input
                min="0"
                type="number"
                placeholder="Entregas"
                value={form.entregas}
                onChange={(event) => setForm({ ...form, entregas: event.target.value })}
              />
              <input
                min="0"
                type="number"
                placeholder="Retornos"
                value={form.retornos}
                onChange={(event) => setForm({ ...form, retornos: event.target.value })}
              />
            </>
          )}
          <select value={form.nota} onChange={(event) => setForm({ ...form, nota: event.target.value })}>
            {[1, 2, 3, 4, 5].map((note) => <option key={note}>{note}</option>)}
          </select>
          <label className="check">
            <input checked={form.penalidade} type="checkbox" onChange={(event) => setForm({ ...form, penalidade: event.target.checked })} />
            Penalidade
          </label>
          {form.penalidade && <input placeholder="Motivo" value={form.motivo_penalidade} onChange={(event) => setForm({ ...form, motivo_penalidade: event.target.value })} required />}
          <button className="primary" type="submit"><Save size={17} /> Salvar</button>
            </form>
          )}

          {form.tipo_lancamento === "mensal" && (
            <form className="panel form-grid entries-form" onSubmit={saveMonthlyEntries}>
          <h2>Lançamento mensal em massa</h2>

          <input
            type="month"
            value={monthlyForm.mes}
            onChange={(event) => setMonthlyForm({ ...monthlyForm, mes: event.target.value })}
          />

          <select
            value={monthlyForm.filtro_turno}
            onChange={(event) =>
              setMonthlyForm({ ...monthlyForm, filtro_turno: event.target.value, notas: {} })
            }
          >
            <option value="Manhã">Manhã</option>
            <option value="Tarde">Tarde</option>
            <option value="Noite">Noite</option>
          </select>

          <select
            value={monthlyForm.tipo_funcionario}
            onChange={(event) =>
              setMonthlyForm({ ...monthlyForm, tipo_funcionario: event.target.value, notas: {} })
            }
          >
            <option value="Funcionário normal">Funcionário normal</option>
            <option value="Entrega">Entrega</option>
          </select>

          {!monthlyIsDelivery && normalizeText(monthlyForm.filtro_turno) === "manha" && (
            <input
              min="0"
              step="0.1"
              type="number"
              placeholder="Toneladas"
              value={monthlyForm.toneladas}
              onChange={(event) =>
                setMonthlyForm({
                  ...monthlyForm,
                  pedidos_separados: 0,
                  pedidos_carregados: 0,
                  toneladas: event.target.value,
                })
              }
            />
          )}

          {!monthlyIsDelivery && normalizeText(monthlyForm.filtro_turno) === "tarde" && (
            <input
              min="0"
              type="number"
              placeholder="Pedidos separados"
              value={monthlyForm.pedidos_separados}
              onChange={(event) =>
                setMonthlyForm({
                  ...monthlyForm,
                  pedidos_separados: event.target.value,
                  pedidos_carregados: 0,
                  toneladas: 0,
                })
              }
            />
          )}

          {!monthlyIsDelivery && normalizeText(monthlyForm.filtro_turno) === "noite" && (
            <input
              min="0"
              type="number"
              placeholder="Pedidos carregados"
              value={monthlyForm.pedidos_carregados}
              onChange={(event) =>
                setMonthlyForm({
                  ...monthlyForm,
                  pedidos_separados: 0,
                  pedidos_carregados: event.target.value,
                  toneladas: 0,
                })
              }
            />
          )}

          {monthlyIsDelivery && (
            <>
              <input
                min="0"
                type="number"
                placeholder="Entregas"
                value={monthlyForm.entregas}
                onChange={(event) =>
                  setMonthlyForm({ ...monthlyForm, entregas: event.target.value })
                }
              />
              <input
                min="0"
                type="number"
                placeholder="Retornos"
                value={monthlyForm.retornos}
                onChange={(event) =>
                  setMonthlyForm({ ...monthlyForm, retornos: event.target.value })
                }
              />
            </>
          )}

          <div className="table-wrap" style={{ gridColumn: "1 / -1" }}>
            <table>
              <thead>
                <tr><th>Funcionário</th><th>Cargo</th><th>Turno</th><th>Nota</th></tr>
              </thead>
              <tbody>
                {monthlyEmployees.map((employee) => (
                  <tr key={employee.id}>
                    <td>{employee.nome}</td>
                    <td>{employee.cargo}</td>
                    <td>{employee.turno}</td>
                    <td>
                      <select
                        value={monthlyForm.notas[employee.id] || 5}
                        onChange={(event) =>
                          setMonthlyForm({
                            ...monthlyForm,
                            notas: {
                              ...monthlyForm.notas,
                              [employee.id]: event.target.value,
                            },
                          })
                        }
                      >
                        {[1, 2, 3, 4, 5].map((note) => (
                          <option key={note}>{note}</option>
                        ))}
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <button className="primary" disabled={!monthlyEmployees.length} type="submit">
            <Save size={17} /> Salvar mensal ({monthlyEmployees.length})
          </button>
            </form>
          )}
        </>
      )}

      {message && <div className="alert">{message}</div>}

      {showHistory && (
        <section className="panel history-panel">
          <div className="section-heading">
            <div>
              <h2>Listagem de lançamentos</h2>
              <p>{filteredEntries.length} lançamento(s) encontrado(s)</p>
            </div>

            <button className="icon-button wide-button" onClick={clearEntryFilters} type="button">
              Limpar filtros
            </button>
          </div>

          <div className="toolbar filter-grid">
            <label>
              Mês
              <input type="month" value={month} onChange={(event) => setMonth(event.target.value)} />
            </label>

            <label>
              Dia
              <input type="date" value={dayFilter} onChange={(event) => setDayFilter(event.target.value)} />
            </label>

            <label>
              Funcionário
              <input
                placeholder="Digite o nome do funcionário"
                value={nameFilter}
                onChange={(event) => setNameFilter(event.target.value)}
              />
            </label>

            <label>
              Tipo
              <select value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)}>
                <option>Todos</option>
                <option value="diario">Diário</option>
                <option value="semanal">Semanal</option>
                <option value="mensal">Mensal</option>
              </select>
            </label>

            <label>
              Turno
              <select value={turnFilter} onChange={(event) => setTurnFilter(event.target.value)}>
                <option>Todos</option>
                <option>Manhã</option>
                <option>Tarde</option>
                <option>Noite</option>
              </select>
            </label>

            <label>
              Bônus mínimo
              <input
                min="0"
                step="0.01"
                type="number"
                value={minBonusFilter}
                onChange={(event) => setMinBonusFilter(event.target.value)}
              />
            </label>

            <label>
              Bônus máximo
              <input
                min="0"
                step="0.01"
                type="number"
                value={maxBonusFilter}
                onChange={(event) => setMaxBonusFilter(event.target.value)}
              />
            </label>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>ID</th><th>Funcionário</th><th>Tipo</th><th>Semana</th><th>Nota</th><th>Bônus</th><th></th></tr>
              </thead>
              <tbody>
                {filteredEntries.map((entry) => (
                  <Fragment key={entry.id}>
                    <tr>
                      <td>{entry.id}</td>
                      <td>{employeeMap[entry.funcionario_id]?.nome || `#${entry.funcionario_id}`}</td>
                      <td>{entry.tipo_lancamento}</td>
                      <td>{entry.semana}</td>
                      <td>{entry.nota}</td>
                      <td>{currency.format(Number(entry.bonus_calculado || 0))}</td>
                      <td>
                        <button 
                          className="icon-button"
                          onClick={() => setEditingEntry(entry)}
                          title="Editar lançamento"
                          type="button"
                        >
                          <Pencil size={16} />
                        </button>

                        <button className="icon-button danger" onClick={() => removeEntry(entry.id)} title="Excluir lançamento" type="button">
                          <Trash2 size={16} />
                        </button>
                      </td>
                    </tr>

                    {editingEntry?.id === entry.id && (
                      <tr className="inline-edit-row">
                        <td colSpan="7">{renderEntryEditForm()}</td>
                      </tr>
                    )}
                  </Fragment>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </section>
  );
}

function Frequencies({ employees, frequencies, load }) {
  const [form, setForm] = useState({
    funcionario_id: "",
    mes: currentMonthInput(),
    status_mes: "Normal",
    houve_ausencia: false,
    data_falta: todayInput(),
    tipo_falta: "Falta",
  });
  const employeeMap = useMemo(() => Object.fromEntries(employees.map((employee) => [employee.id, employee])), [employees]);
  const [message, setMessage] = useState("");
  const [editingFrequency, setEditingFrequency] = useState(null);

  function frequencyPayload(source) {
    const hasAbsence = source.status_mes === "Normal" && source.houve_ausencia;

    return {
      funcionario_id: Number(source.funcionario_id),
      mes: hasAbsence ? source.data_falta.slice(0, 7) : source.mes,
      ausencias: hasAbsence ? 1 : 0,
      data_falta: hasAbsence ? source.data_falta : null,
      tipo_falta: hasAbsence ? source.tipo_falta : null,
      status_mes: source.status_mes,
    };
  }

  async function saveFrequency(event) {
    event.preventDefault();
    try {
      await api.post("/frequencias", frequencyPayload(form));
      await load();
      setMessage("Frequência salva.");
    } catch (err) {
      setMessage(errorMessage(err));
    }
  }

  function startEditFrequency(frequency) {
    setEditingFrequency({
      id: frequency.id,
      funcionario_id: String(frequency.funcionario_id),
      mes: frequency.mes || currentMonthInput(),
      status_mes: frequency.status_mes || "Normal",
      houve_ausencia: Number(frequency.ausencias || 0) > 0,
      data_falta: frequency.data_falta || todayInput(),
      tipo_falta: frequency.tipo_falta || "Falta",
    });
  }

  async function updateFrequency(event) {
    event.preventDefault();
    setMessage("");

    try {
      await api.put(`/frequencias/${editingFrequency.id}`, frequencyPayload(editingFrequency));
      setEditingFrequency(null);
      await load();
      setMessage("Frequência atualizada.");
    } catch (err) {
      setMessage(errorMessage(err));
    }
  }

  async function removeFrequency(id) {
    if (!confirm("Excluir frequência?")) return;
    setMessage("");

    try {
      await api.delete(`/frequencias/${id}`);
      await load();
      setMessage("Frequência excluída.");
    } catch (err) {
      setMessage(errorMessage(err));
    }
  }

  function renderFrequencyEditForm() {
    if (!editingFrequency) return null;

    return (
      <form className="inline-edit-form form-grid" onSubmit={updateFrequency}>
        <h2>Editar frequência</h2>

        <select value={editingFrequency.funcionario_id} onChange={(event) => setEditingFrequency({ ...editingFrequency, funcionario_id: event.target.value })} required>
          <option value="">Funcionário</option>
          {employees.map((employee) => <option key={employee.id} value={employee.id}>{employeeLabel(employee)}</option>)}
        </select>

        <input type="month" value={editingFrequency.mes} onChange={(event) => setEditingFrequency({ ...editingFrequency, mes: event.target.value })} />

        <select
          value={editingFrequency.status_mes}
          onChange={(event) =>
            setEditingFrequency({
              ...editingFrequency,
              status_mes: event.target.value,
              houve_ausencia: event.target.value === "Normal" ? editingFrequency.houve_ausencia : false,
            })
          }
        >
          <option>Normal</option>
          <option>Férias</option>
        </select>

        {editingFrequency.status_mes === "Normal" && (
          <>
            <label className="check">
              <input checked={editingFrequency.houve_ausencia} type="checkbox" onChange={(event) => setEditingFrequency({ ...editingFrequency, houve_ausencia: event.target.checked })} />
              Houve ausência
            </label>

            {editingFrequency.houve_ausencia && (
              <>
                <input type="date" value={editingFrequency.data_falta} onChange={(event) => setEditingFrequency({ ...editingFrequency, data_falta: event.target.value })} />
                <select value={editingFrequency.tipo_falta} onChange={(event) => setEditingFrequency({ ...editingFrequency, tipo_falta: event.target.value })}>
                  <option>Falta</option>
                  <option>Atestado</option>
                  <option>Licença legal</option>
                </select>
              </>
            )}
          </>
        )}

        <button className="primary" type="submit"><Save size={17} /> Salvar alterações</button>
        <button className="icon-button" onClick={() => setEditingFrequency(null)} type="button">X</button>
      </form>
    );
  }

  return (
    <section className="view">
      <form className="panel form-grid" onSubmit={saveFrequency}>
        <h2>Registrar frequência</h2>
        <select value={form.funcionario_id} onChange={(event) => setForm({ ...form, funcionario_id: event.target.value })} required>
          <option value="">Funcionário</option>
          {employees.map((employee) => <option key={employee.id} value={employee.id}>{employeeLabel(employee)}</option>)}
        </select>
        <input type="month" value={form.mes} onChange={(event) => setForm({ ...form, mes: event.target.value })} />
        <select value={form.status_mes} onChange={(event) => setForm({ ...form, status_mes: event.target.value })}>
          <option>Normal</option>
          <option>Férias</option>
        </select>
        {form.status_mes === "Normal" && (
          <>
            <label className="check">
              <input checked={form.houve_ausencia} type="checkbox" onChange={(event) => setForm({ ...form, houve_ausencia: event.target.checked })} />
              Houve ausência
            </label>
            {form.houve_ausencia && (
              <>
                <input type="date" value={form.data_falta} onChange={(event) => setForm({ ...form, data_falta: event.target.value })} />
                <select value={form.tipo_falta} onChange={(event) => setForm({ ...form, tipo_falta: event.target.value })}>
                  <option>Falta</option>
                  <option>Atestado</option>
                  <option>Licença legal</option>
                </select>
              </>
            )}
          </>
        )}
        <button className="primary" type="submit"><Save size={17} /> Salvar</button>
      </form>

      {message && <div className="alert">{message}</div>}

      <div className="table-wrap">
        <table>
          <thead>
            <tr><th>ID</th><th>Funcionário</th><th>Mês</th><th>Status</th><th>Ausências</th><th>Dia</th><th>Tipo</th><th></th></tr>
          </thead>
          <tbody>
            {frequencies.map((frequency) => (
              <Fragment key={frequency.id}>
                <tr>
                  <td>{frequency.id}</td>
                  <td>{employeeMap[frequency.funcionario_id]?.nome || `#${frequency.funcionario_id}`}</td>
                  <td>{frequency.mes}</td>
                  <td>{frequency.status_mes}</td>
                  <td>{frequency.ausencias}</td>
                  <td>{frequency.data_falta || "-"}</td>
                  <td>{frequency.tipo_falta || "-"}</td>
                  <td>
                    <button
                      className="icon-button"
                      onClick={() => startEditFrequency(frequency)}
                      title="Editar frequência"
                      type="button"
                    >
                      <Pencil size={16} />
                    </button>

                    <button
                      className="icon-button danger"
                      onClick={() => removeFrequency(frequency.id)}
                      title="Excluir frequência"
                      type="button"
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>

                {editingFrequency?.id === frequency.id && (
                  <tr className="inline-edit-row">
                    <td colSpan="8">{renderFrequencyEditForm()}</td>
                  </tr>
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function Closing() {
  const [month, setMonth] = useState(currentMonthInput());
  const [closing, setClosing] = useState([]);
  const [message, setMessage] = useState("");

  async function calculate() {
    setMessage("");
    try {
      setClosing(await api.get(`/fechamento/${month}`));
    } catch (err) {
      setMessage(errorMessage(err));
    }
  }

  useEffect(() => {
    calculate();
  }, []);

  return (
    <section className="view">
      <div className="toolbar">
        <label>
          Mês
          <input type="month" value={month} onChange={(event) => setMonth(event.target.value)} />
        </label>
        <button className="primary" onClick={calculate} type="button"><BarChart3 size={17} /> Calcular</button>
        <a className="button-link" href={downloadUrl(`/exportar-fechamento/${month}`)}>
          <FileSpreadsheet size={17} /> Excel
        </a>
      </div>

      {message && <div className="alert error">{message}</div>}

      <div className="table-wrap">
        <table>
          <thead>
            <tr><th>Funcionário</th><th>Cargo</th><th>Status</th><th>Ausências</th><th>Lançamentos</th><th>Assiduidade</th><th>Bônus final</th></tr>
          </thead>
          <tbody>
            {closing.map((item) => (
              <tr key={item.funcionario_id}>
                <td>{item.funcionario}</td>
                <td>{item.cargo}</td>
                <td><span className={item.elegivel ? "badge ok" : "badge danger"}>{item.status_mes === "Férias" ? "Férias" : item.elegivel ? "Elegível" : "Bloqueado"}</span></td>
                <td>{item.ausencias}</td>
                <td>{item.quantidade_lancamentos}</td>
                <td>{currency.format(Number(item.assiduidade || 0))}</td>
                <td><strong>{currency.format(Number(item.bonus_final || 0))}</strong></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function Rules() {
  return (
    <section className="view">
      <div className="panel rules-grid">
        <h2>Regras de Negocio</h2>

        <article>
          <h3>Assiduidade mensal</h3>
          <p>Todo funcionário começa o mês com R$ 150,00 de assiduidade. Se tiver qualquer ausência no mês, perde o valor.</p>
        </article>

        <article>
          <h3>Regra por turno</h3>
          <p>Manhã recebe por toneladas: R$ 2,00 por tonelada.</p>
          <p>Tarde recebe por pedidos separados: R$ 0,10 por pedido.</p>
          <p>Noite recebe por pedidos carregados: R$ 0,10 por pedido.</p>
        </article>

        <article>
          <h3>Funcionários de entrega</h3>
          <p>Motorista e ajudante ficam agrupados como Entrega.</p>
        </article>

        <article>
          <h3>Nota de desempenho</h3>
          <p>Nota 5: 100%, Nota 4: 90%, Nota 3: 80%, Nota 2: 50%, Nota 1: 20%.</p>
        </article>

        <article>
          <h3>Penalidade de 50%</h3>
          <p>Quando marcada, a bonificação é reduzida pela metade e o motivo deve ser informado.</p>
        </article>
      </div>
    </section>
  );
}
