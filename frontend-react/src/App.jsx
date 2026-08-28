import {
  BarChart3,
  CalendarCheck,
  ChevronDown,
  CircleMinus,
  Clock,
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
  MoreVertical,
  Moon,
  Percent,
  SlidersHorizontal,
  Star,
  Sun,
  Truck
} from "lucide-react";
import { Fragment, useEffect, useMemo, useState } from "react";
import { api, downloadUrl } from "./api";
import {
  belongsToMonth,
  currency,
  currentMonthInput,
  employeeLabel,
  errorMessage,
  isValidMonthInput,
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

function normalizeDeliveryType(value) {
  const normalized = (value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim()
    .toLowerCase();

  return normalized === "entrega" ? "Entrega" : "Não se aplica";
}

const bonusCriteria = [
  { id: "pedidos_separados", label: "Pedidos separados", type: "number", step: "1" },
  { id: "pedidos_carregados", label: "Pedidos carregados", type: "number", step: "1" },
  { id: "toneladas", label: "Toneladas", type: "number", step: "0.1" },
  { id: "entregas", label: "Entregas", type: "number", step: "1" },
  { id: "retornos", label: "Retornos", type: "number", step: "1" },
];

const USERS = {
  admin: "8599256",
  iann: "1234",
  valesca: "Rhcem123@",
  paulo: "Cempaulo123@",
  romario: "Cemromario123@",
  gabriel: "Cemgabriel123@",
  ronilson: "Cemroni123@",
  kayke: "Cemkayke123@",
  junior: "Cemjunior123@",
  rafael: "Cemrafa123@"
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
  const [receipts, setReceipts] = useState([]);
  const [frequencies, setFrequencies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [funcionarios, lancamentos, recebimentos, frequencias] = await Promise.all([
        api.get("/funcionarios"),
        api.get("/lancamentos-semanais"),
        api.get("/recebimentos-toneladas"),
        api.get("/frequencias"),
      ]);
      setEmployees(funcionarios);
      setEntries(lancamentos);
      setReceipts(recebimentos);
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

  return { employees, entries, receipts, frequencies, loading, error, load };
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
        {!data.loading && activeTab === "lancamentos" && <Entries {...data} mode="form" loggedUser={loggedUser} />}
        {!data.loading && activeTab === "historico-lancamentos" && <Entries {...data} mode="history" loggedUser={loggedUser} />}
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
  const [selectedMonth, setSelectedMonth] = useState(month);
  const [closing, setClosing] = useState([]);
  const [error, setError] = useState("");
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [periodStart, setPeriodStart] = useState("");
  const [periodEnd, setPeriodEnd] = useState("");
  const [dateScope, setDateScope] = useState("Todos");
  const [weekFilter, setWeekFilter] = useState("Todos");

  useEffect(() => {
    setError("");
    api
      .get(`/fechamento/${selectedMonth}`)
      .then((data) => setClosing(Array.isArray(data) ? data : []))
      .catch((err) => setError(errorMessage(err)));
  }, [selectedMonth]);

  const monthEntries = entries.filter((entry) => belongsToMonth(entry, selectedMonth));
  const hasDateRange = Boolean(periodStart || periodEnd);
  const selectedYear = selectedMonth.slice(0, 4);
  const scopeEntries = dateScope === "Ano" || hasDateRange ? entries : monthEntries;
  const filteredEntries = scopeEntries.filter((entry) => {
    const entryDate = entry.data_lancamento || "";
    const entryMonth = entryDate.slice(0, 7);
    const entryYear = entryDate.slice(0, 4);

    const matchesDateScope =
      dateScope === "Todos" ||
      (dateScope === "Ano" && entryYear === selectedYear) ||
      (dateScope === "Mês" && entryMonth === selectedMonth) ||
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
  const weeks = [...new Set(scopeEntries.map((entry) => entry.semana).filter(Boolean))].sort();
  const weekOptionsKey = weeks.join("|");
  const filteredEmployeeIds = new Set(dashboardEntries.map((entry) => entry.funcionario_id));
  const employeeById = new Map(employees.map((employee) => [employee.id, employee]));
  const closingByEmployee = new Map(closing.map((item) => [item.funcionario_id, item]));
  const filteredRankingItems = [...dashboardEntries.reduce((items, entry) => {
    const employee = employeeById.get(entry.funcionario_id);
    if (!employee?.ativo) return items;

    const current = items.get(entry.funcionario_id) || {
      funcionario_id: entry.funcionario_id,
      funcionario: employee?.nome || `Funcionário #${entry.funcionario_id}`,
      cargo: employee?.cargo || "-",
      bonus_final: 0,
      quantidade_lancamentos: 0,
      elegivel: closingByEmployee.get(entry.funcionario_id)?.elegivel ?? true,
      assiduidade: 0,
    };

    current.bonus_final += Number(entry.bonus_calculado || 0);
    current.quantidade_lancamentos += 1;
    items.set(entry.funcionario_id, current);
    return items;
  }, new Map()).values()];
  const useFilteredRanking = hasAdvancedFilters && !(dateScope === "Mês" && !periodStart && !periodEnd && weekFilter === "Todos");
  const rankingItems = useFilteredRanking ? filteredRankingItems : closing;
  const activeEmployees = employees.filter((employee) => employee.ativo);
  const visibleActiveEmployees = hasAdvancedFilters
    ? activeEmployees.filter((employee) => filteredEmployeeIds.has(employee.id))
    : activeEmployees;
  const totalBonus = rankingItems.reduce((sum, item) => sum + Number(item.bonus_final || 0), 0);
  const blocked = rankingItems.filter((item) => !item.elegivel).length;
  const eligible = rankingItems.filter((item) => item.elegivel).length;
  const assiduity = rankingItems.reduce((sum, item) => sum + Number(item.assiduidade || 0), 0);

  useEffect(() => {
    const weekOptions = weekOptionsKey ? weekOptionsKey.split("|") : [];
    if (weekFilter !== "Todos" && !weekOptions.includes(weekFilter)) {
      setWeekFilter("Todos");
    }
  }, [weekFilter, weekOptionsKey]);

  function clearDashboardFilters() {
    setPeriodStart("");
    setPeriodEnd("");
    setDateScope("Todos");
    setWeekFilter("Todos");
  }

  function changeDashboardMonth(value) {
    setMonth(value);
    if (isValidMonthInput(value)) {
      setSelectedMonth(value);
    }
  }

  return (
    <section className="view">
      <div className="dashboard-filters">
        <div className="toolbar">
          <label>
            Mês
            <input type="month" value={month} onChange={(event) => changeDashboardMonth(event.target.value)} />
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

  function startEditing(employee) {
    setEditing({
      ...employee,
      tipo_entrega: normalizeDeliveryType(employee.tipo_entrega),
    });
  }

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
      tipo_entrega: normalizeDeliveryType(editing.tipo_entrega),
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
          <option>Horário comercial</option>
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
        <table className="employees-table">
          <thead>
            <tr><th>ID</th><th>Nome</th><th>Cargo</th><th>Turno</th><th>Entrega</th><th>Status</th><th></th></tr>
          </thead>
          <tbody>
            {filtered.map((employee) => (
              <Fragment key={employee.id}>
                <tr>
                  <td data-label="ID">{employee.id}</td>
                  <td data-label="Nome">{employee.nome}</td>
                  <td data-label="Cargo">{employee.cargo}</td>
                  <td data-label="Turno">{employee.turno}</td>
                  <td data-label="Entrega">{employee.tipo_entrega}</td>
                  <td data-label="Status"><span className={employee.ativo ? "badge ok" : "badge muted"}>{employee.ativo ? "Ativo" : "Inativo"}</span></td>
                  <td className="row-actions" data-label="Ações">
                    <button
                      className="icon-button"
                      onClick={() => startEditing(employee)}
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
                          <option>Horário comercial</option>
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

function Entries({ employees, entries, receipts = [], load, mode = "all", loggedUser = "" }) {
  const [form, setForm] = useState({
    funcionario_id: "",
    tipo_lancamento: "semanal",
    data_lancamento: todayInput(),
    pedidos_separados: 0,
    pedidos_carregados: 0,
    toneladas: 0,
    numero_carregamento: "",
    numero_nota_fiscal: "",
    nota_fiscal_pdf: null,
    nota_fiscal_pdf_nome: null,
    entregas: 0,
    retornos: 0,
    nota: 3,
    penalidade: false,
    motivo_penalidade: "",
    ajuste_operacao: "adicionar",
    ajuste_personalizado_descricao: "pedidos_separados",
    ajuste_personalizado_valor: 0,
    ajustes_personalizados: [{ criterio: "pedidos_separados", operacao: "adicionar" }],
  });
  const [month, setMonth] = useState(currentMonthInput());
  const [dayFilter, setDayFilter] = useState("");
  const [nameFilter, setNameFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("Todos");
  const [turnFilter, setTurnFilter] = useState("Todos");
  const [minBonusFilter, setMinBonusFilter] = useState("");
  const [maxBonusFilter, setMaxBonusFilter] = useState("");
  const [message, setMessage] = useState("");
  const [entryMenuOpen, setEntryMenuOpen] = useState(false);
  const [customEntryEnabled, setCustomEntryEnabled] = useState(false);
  const [loadingNumberFieldsEnabled, setLoadingNumberFieldsEnabled] = useState(false);
  const [invoiceFieldsEnabled, setInvoiceFieldsEnabled] = useState(false);
  const [receiptParticipants, setReceiptParticipants] = useState({});
  const [receiptMenuOpen, setReceiptMenuOpen] = useState(null);
  const [receiptExtraEmployeeId, setReceiptExtraEmployeeId] = useState({});
  const [editingReceipt, setEditingReceipt] = useState(null);
  const employeeMap = useMemo(() => Object.fromEntries(employees.map((employee) => [employee.id, employee])), [employees]);
  const [editingEntry, setEditingEntry] = useState(null);
  const [editingReceiptEntryId, setEditingReceiptEntryId] = useState(null);
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

  function isSupervisorUser(user) {
    return ["admin", "iann", "valesca", "paulo", "romario", "gabriel", "junior"].includes(normalizeText(user));
  }

  function isExpeditionUser(user) {
    return ["ronilson", "kayke"].includes(normalizeText(user));
  }

  function entryTypeLabel(type) {
    const labels = {
      diario: "Diário",
      semanal: "Semanal",
      mensal: "Mensal",
      avaliacao_semanal: "Avaliação semanal",
      recebimento_toneladas: "Recebimento toneladas",
    };
    return labels[normalizeText(type)] || type || "-";
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

  function isMorningEmployee(employee) {
    return normalizeText(employee?.turno) === "manha";
  }

  function isDefaultReceiptEmployee(employee) {
    return isMorningEmployee(employee) && !isDeliveryEmployee(employee);
  }

  function receivesByTonnes(employee) {
    return isMorningEmployee(employee) && !isDeliveryEmployee(employee);
  }

  function receiptVisibleEmployees(receipt) {
    const selected = receiptParticipants[receipt.id] || {};
    return employees.filter((employee) => (
      employee.ativo && (isDefaultReceiptEmployee(employee) || selected[employee.id])
    ));
  }

  function receiptExtraEmployeeOptions(receipt) {
    const selected = receiptParticipants[receipt.id] || {};
    return employees.filter((employee) => (
      employee.ativo && !isDefaultReceiptEmployee(employee) && !selected[employee.id]
    ));
  }

  function receiptParticipantIds(receipt) {
    try {
      const parsed = JSON.parse(receipt?.participantes || "[]");
      return Array.isArray(parsed) ? parsed.map((id) => Number(id)).filter(Boolean) : [];
    } catch {
      return [];
    }
  }

  function sameReceiptField(first, second) {
    return String(first || "") === String(second || "");
  }

  function receiptMatchesEntry(receipt, entry) {
    return (
      normalizeText(entry.tipo_lancamento) === "recebimento_toneladas" &&
      normalizeText(receipt.status) === "distribuido" &&
      receipt.semana === entry.semana &&
      sameReceiptField(receipt.data_lancamento, entry.data_lancamento) &&
      Number(receipt.toneladas || 0) === Number(entry.toneladas || 0) &&
      sameReceiptField(receipt.numero_carregamento, entry.numero_carregamento) &&
      sameReceiptField(receipt.numero_nota_fiscal, entry.numero_nota_fiscal)
    );
  }

  function receiptForEntry(entry) {
    if (normalizeText(entry.tipo_lancamento) !== "recebimento_toneladas") return null;

    const exactReceipt = receipts.find((receipt) => (
      receiptMatchesEntry(receipt, entry) &&
      receiptParticipantIds(receipt).includes(Number(entry.funcionario_id))
    ));
    if (exactReceipt) return exactReceipt;

    return receipts.find((receipt) => receiptMatchesEntry(receipt, entry)) || null;
  }

  function entryUserInfo(entry) {
    const receipt = receiptForEntry(entry);
    if (!receipt) {
      return {
        launchedBy: entry.usuario_lancamento || "-",
        chosenBy: "-",
      };
    }

    return {
      launchedBy: receipt.usuario_lancamento || "-",
      chosenBy: entry.usuario_lancamento || "-",
    };
  }

  function participantStateForReceipt(receipt) {
    return Object.fromEntries(receiptParticipantIds(receipt).map((id) => [id, true]));
  }

  function toggleReceiptParticipant(receiptId, employeeId, selected) {
    setReceiptParticipants((current) => ({
      ...current,
      [receiptId]: {
        ...(current[receiptId] || {}),
        [employeeId]: selected,
      },
    }));
  }

  function addReceiptExtraEmployee(receiptId) {
    const employeeId = Number(receiptExtraEmployeeId[receiptId] || 0);
    if (!employeeId) return;

    toggleReceiptParticipant(receiptId, employeeId, true);
    setReceiptExtraEmployeeId((current) => ({ ...current, [receiptId]: "" }));
    setReceiptMenuOpen(null);
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
  const selectedEmployeeReceivesTonnes = shouldShowCriterion(
    customEntryEnabled ? form : withoutCustomAdjustments(form),
    selectedEmployeeTurn,
    selectedEmployeeIsDelivery,
    "toneladas",
  );
  const showInvoiceFields = invoiceFieldsEnabled && selectedEmployeeReceivesTonnes;
  const showLoadingNumberFields = loadingNumberFieldsEnabled && Boolean(form.funcionario_id);
  const editingEmployeeReceivesTonnes = editingEntry && shouldShowCriterion(
    editingEntry,
    editingEmployeeTurn,
    editingEmployeeIsDelivery,
    "toneladas",
  );
  const monthlyIsDelivery = normalizeText(monthlyForm.tipo_funcionario) === "entrega";
  const monthlyIsCommercialHours = normalizeText(monthlyForm.filtro_turno) === "horario comercial";
  const isReceiptEntry = form.tipo_lancamento === "recebimento_toneladas";
  const isEvaluationEntry = form.tipo_lancamento === "avaliacao_semanal";
  const isNormalEntry = ["semanal", "diario"].includes(form.tipo_lancamento);
  const supervisorEntry = isSupervisorUser(loggedUser);
  const availableEntryEmployees = employees.filter((employee) => (
    employee.ativo && (!isNormalEntry || !receivesByTonnes(employee) || supervisorEntry)
  ));
  const canCreateSupervisorEntries = isSupervisorUser(loggedUser);
  const canChooseReceiptParticipants = isExpeditionUser(loggedUser);
  const canManageEntries = !canChooseReceiptParticipants;
  const canViewPendingReceipts = canChooseReceiptParticipants || canCreateSupervisorEntries;
  const pendingReceipts = receipts.filter((receipt) => (
    normalizeText(receipt.status) === "pendente" &&
    (canChooseReceiptParticipants || normalizeText(receipt.usuario_lancamento) === normalizeText(loggedUser))
  ));
  const showForm = mode !== "history";
  const showHistory = mode !== "form";

  function normalizeCriterionId(value) {
    const normalized = normalizeText(value);
    return bonusCriteria.find((criterion) => (
      normalizeText(criterion.id) === normalized ||
      normalizeText(criterion.label) === normalized
    ))?.id || value;
  }

  function normalizeAdjustment(item) {
    return {
      criterio: normalizeCriterionId(item.criterio),
      operacao: normalizeText(item.operacao) === "retirar" ? "retirar" : "adicionar",
    };
  }

  function customAdjustments(source) {
    if (Array.isArray(source.ajustes_personalizados)) {
      return source.ajustes_personalizados
        .filter((item) => item?.criterio && item?.operacao)
        .map(normalizeAdjustment);
    }

    if (source.ajuste_personalizado_itens) {
      try {
        const parsed = JSON.parse(source.ajuste_personalizado_itens);
        if (Array.isArray(parsed)) {
          return parsed
            .filter((item) => item?.criterio && item?.operacao)
            .map(normalizeAdjustment);
        }
      } catch {
        return [];
      }
    }

    if (source.ajuste_personalizado_descricao && source.ajuste_personalizado_operacao) {
      return [normalizeAdjustment({
        criterio: source.ajuste_personalizado_descricao,
        operacao: source.ajuste_personalizado_operacao,
      })];
    }

    return [];
  }

  function normalizedCustomAdjustments(source) {
    return customAdjustments(source)
      .filter((item) => item.criterio && item.operacao)
      .map((item) => ({ criterio: item.criterio, operacao: item.operacao }));
  }

  function hasCustomCriterion(source, criterion, operation) {
    return customAdjustments(source).some((item) => (
      normalizeCriterionId(item.criterio) === criterion && (!operation || item.operacao === operation)
    ));
  }

  function isCriterionRemoved(source, criterion) {
    return hasCustomCriterion(source, criterion, "retirar");
  }

  function isCriterionAdded(source, criterion) {
    return hasCustomCriterion(source, criterion, "adicionar");
  }

  function criterionValue(source, criterion, disabled = false) {
    if (disabled || isCriterionRemoved(source, criterion)) return 0;
    return Number(source[criterion] || 0);
  }

  function customCriterionLabel(criterion) {
    return bonusCriteria.find((item) => item.id === criterion)?.label || criterion || "-";
  }

  function customAdjustmentSummary(source) {
    const adjustments = normalizedCustomAdjustments(source);
    if (!adjustments.length) return "-";

    return adjustments
      .map((item) => `${item.operacao === "retirar" ? "Retira" : "Adiciona"} ${customCriterionLabel(item.criterio)}`)
      .join(", ");
  }

  function shouldShowCriterion(source, employeeTurn, isDelivery, criterion) {
    if (employeeTurn === "horario comercial") return false;
    if (isCriterionRemoved(source, criterion)) return false;
    if (isCriterionAdded(source, criterion)) return true;
    if (criterion === "toneladas") return !isDelivery && employeeTurn === "manha";
    if (criterion === "pedidos_separados") return !isDelivery && employeeTurn === "tarde";
    if (criterion === "pedidos_carregados") return !isDelivery && employeeTurn === "noite";
    if (["entregas", "retornos"].includes(criterion)) return isDelivery;
    return false;
  }

  function updateMetric(source, setter, criterion, value) {
    setter({ ...source, [criterion]: value });
  }

  function metricInputValue(source, criterion) {
    return source[criterion] ?? "";
  }

  function selectInvoicePdf(file, setter) {
    if (!file) {
      setter((current) => ({ ...current, nota_fiscal_pdf: null, nota_fiscal_pdf_nome: null }));
      return;
    }
    if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
      setMessage("Selecione um arquivo PDF para a nota fiscal.");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setMessage("O PDF da nota fiscal deve ter no máximo 10 MB.");
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      const base64 = String(reader.result || "").split(",")[1] || null;
      setter((current) => ({ ...current, nota_fiscal_pdf: base64, nota_fiscal_pdf_nome: file.name }));
      setMessage("");
    };
    reader.onerror = () => setMessage("Não foi possível ler o PDF da nota fiscal.");
    reader.readAsDataURL(file);
  }

  function addCustomAdjustment(source, setter) {
    setter({
      ...source,
      ajustes_personalizados: [
        ...customAdjustments(source),
        { criterio: "pedidos_separados", operacao: "adicionar" },
      ],
    });
  }

  function updateCustomAdjustment(source, setter, index, field, value) {
    const adjustments = customAdjustments(source).map((item, currentIndex) => (
      currentIndex === index ? { ...item, [field]: value } : item
    ));
    setter({ ...source, ajustes_personalizados: adjustments });
  }

  function removeCustomAdjustment(source, setter, index) {
    const adjustments = customAdjustments(source).filter((_, currentIndex) => currentIndex !== index);
    setter({ ...source, ajustes_personalizados: adjustments });
  }

  function withoutCustomAdjustments(source) {
    return { ...source, ajustes_personalizados: [], ajuste_personalizado_itens: null };
  }

  function changeEntryType(type) {
    const nextIsNormalEntry = ["semanal", "diario"].includes(type);
    const currentEmployee = form.funcionario_id ? employeeMap[form.funcionario_id] : null;
    setForm((current) => ({
      ...current,
      tipo_lancamento: type,
      funcionario_id: nextIsNormalEntry && receivesByTonnes(currentEmployee) && !supervisorEntry ? "" : current.funcionario_id,
      pedidos_separados: 0,
      pedidos_carregados: 0,
      toneladas: 0,
      entregas: 0,
      retornos: 0,
      numero_carregamento: "",
      numero_nota_fiscal: "",
      nota_fiscal_pdf: null,
      nota_fiscal_pdf_nome: null,
    }));
    setLoadingNumberFieldsEnabled(false);
    setInvoiceFieldsEnabled(false);
  }

  async function saveEntry(event) {
    event.preventDefault();
    if (isReceiptEntry) {
      setMessage("");
      try {
        await api.post("/recebimentos-toneladas", {
          semana: weekLabel(form.data_lancamento),
          usuario_lancamento: loggedUser || null,
          data_lancamento: form.data_lancamento,
          toneladas: Number(form.toneladas || 0),
          numero_carregamento: form.numero_carregamento || null,
          numero_nota_fiscal: form.numero_nota_fiscal || null,
          nota_fiscal_pdf: form.nota_fiscal_pdf || null,
          nota_fiscal_pdf_nome: form.nota_fiscal_pdf_nome || null,
        });
        await load();
        setForm((current) => ({
          ...current,
          toneladas: 0,
          numero_carregamento: "",
          numero_nota_fiscal: "",
          nota_fiscal_pdf: null,
          nota_fiscal_pdf_nome: null,
        }));
        setMessage("Recebimento enviado para a expedição escolher os participantes.");
      } catch (err) {
        setMessage(errorMessage(err));
      }
      return;
    }

    if (isNormalEntry && receivesByTonnes(selectedEmployee) && !supervisorEntry) {
      setMessage("Funcionários que recebem por toneladas devem entrar apenas em Recebimento de toneladas.");
      return;
    }

    const adjustments = customEntryEnabled ? normalizedCustomAdjustments(form) : [];
    const formRules = customEntryEnabled ? form : withoutCustomAdjustments(form);
    const firstAdjustment = adjustments[0] || {};
    const payload = {
      ...form,
      funcionario_id: Number(form.funcionario_id),
      semana: weekLabel(form.data_lancamento),
      usuario_lancamento: loggedUser || null,
      data_lancamento: form.data_lancamento,
      pedidos_separados: isEvaluationEntry ? 0 : criterionValue(formRules, "pedidos_separados"),
      pedidos_carregados: isEvaluationEntry ? 0 : criterionValue(formRules, "pedidos_carregados"),
      toneladas: isEvaluationEntry ? 0 : criterionValue(formRules, "toneladas", selectedEmployeeIsDelivery && !isCriterionAdded(formRules, "toneladas")),
      numero_carregamento: showLoadingNumberFields ? form.numero_carregamento || null : null,
      entregas: isEvaluationEntry ? 0 : criterionValue(formRules, "entregas"),
      retornos: isEvaluationEntry ? 0 : criterionValue(formRules, "retornos"),
      numero_nota_fiscal: showInvoiceFields ? form.numero_nota_fiscal || null : null,
      nota_fiscal_pdf: showInvoiceFields ? form.nota_fiscal_pdf || null : null,
      nota_fiscal_pdf_nome: showInvoiceFields ? form.nota_fiscal_pdf_nome || null : null,
      nota: isEvaluationEntry ? Number(form.nota) : 5,
      penalidade: isEvaluationEntry ? false : form.penalidade,
      motivo_penalidade: !isEvaluationEntry && form.penalidade ? form.motivo_penalidade : null,
      ajuste_personalizado_descricao: isEvaluationEntry ? null : firstAdjustment.criterio || null,
      ajuste_personalizado_operacao: isEvaluationEntry ? null : firstAdjustment.operacao || null,
      ajuste_personalizado_valor: !isEvaluationEntry && firstAdjustment.criterio ? criterionValue(form, firstAdjustment.criterio) : 0,
      ajuste_personalizado_itens: !isEvaluationEntry && adjustments.length ? JSON.stringify(adjustments) : null,
    };
    setMessage("");
    try {
      const saved = await api.post("/lancamentos-semanais", payload);
      await load();
      setCustomEntryEnabled(false);
      setLoadingNumberFieldsEnabled(false);
      setInvoiceFieldsEnabled(false);
      setForm((current) => ({
        ...current,
        pedidos_separados: 0,
        pedidos_carregados: 0,
        toneladas: 0,
        numero_carregamento: "",
        entregas: 0,
        retornos: 0,
        numero_nota_fiscal: "",
        nota_fiscal_pdf: null,
        nota_fiscal_pdf_nome: null,
        ajustes_personalizados: [{ criterio: "pedidos_separados", operacao: "adicionar" }],
      }));
      setMessage(isEvaluationEntry ? "Avaliação semanal salva." : `Lançamento salvo. Bônus: ${currency.format(Number(saved.bonus_calculado || 0))}`);
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
        usuario_lancamento: loggedUser || null,
        pedidos_separados: monthlyIsCommercialHours ? 0 : Number(monthlyForm.pedidos_separados),
        pedidos_carregados: monthlyIsCommercialHours ? 0 : Number(monthlyForm.pedidos_carregados),
        toneladas: monthlyIsDelivery || monthlyIsCommercialHours ? 0 : Number(monthlyForm.toneladas),
        entregas: monthlyIsCommercialHours ? 0 : Number(monthlyForm.entregas || 0),
        retornos: monthlyIsCommercialHours ? 0 : Number(monthlyForm.retornos || 0),
        notas: notes,
      });

      await load();
      setMessage(`Lançamento mensal salvo para ${saved.length} funcionário(s).`);
    } catch (err) {
      setMessage(errorMessage(err));
    }
  }

  async function saveReceiptParticipants(receiptId) {
    const receipt = receipts.find((item) => item.id === receiptId);
    const isDistributed = normalizeText(receipt?.status) === "distribuido";
    const selectedIds = Object.entries(receiptParticipants[receiptId] || {})
      .filter(([, selected]) => selected)
      .map(([id]) => Number(id));

    if (!selectedIds.length) {
      setMessage("Selecione ao menos um participante do recebimento.");
      return false;
    }

    setMessage("");
    try {
      const save = isDistributed ? api.put : api.post;
      const saved = await save(`/recebimentos-toneladas/${receiptId}/participantes`, {
        funcionario_ids: selectedIds,
        usuario_lancamento: loggedUser || null,
      });
      await load();
      setReceiptParticipants((current) => ({ ...current, [receiptId]: {} }));
      setEditingReceiptEntryId(null);
      setMessage(isDistributed
        ? `Participantes atualizados para ${saved.length} participante(s).`
        : `Recebimento distribuído para ${saved.length} participante(s).`
      );
      return true;
    } catch (err) {
      setMessage(errorMessage(err));
      return false;
    }
  }

  async function updateReceipt(event) {
    event.preventDefault();
    setMessage("");

    try {
      await api.put(`/recebimentos-toneladas/${editingReceipt.id}`, {
        semana: editingReceipt.semana,
        data_lancamento: editingReceipt.data_lancamento || null,
        toneladas: Number(editingReceipt.toneladas || 0),
        numero_carregamento: editingReceipt.numero_carregamento || null,
        numero_nota_fiscal: editingReceipt.numero_nota_fiscal || null,
        nota_fiscal_pdf: editingReceipt.nota_fiscal_pdf || null,
        nota_fiscal_pdf_nome: editingReceipt.nota_fiscal_pdf_nome || null,
      });
      setEditingReceipt(null);
      await load();
      setMessage("Recebimento atualizado.");
    } catch (err) {
      setMessage(errorMessage(err));
    }
  }

  async function removeReceipt(id) {
    if (!confirm("Excluir recebimento pendente?")) return;

    setMessage("");
    try {
      await api.delete(`/recebimentos-toneladas/${id}`);
      if (editingReceipt?.id === id) setEditingReceipt(null);
      await load();
      setMessage("Recebimento excluído.");
    } catch (err) {
      setMessage(errorMessage(err));
    }
  }

  function editReceiptParticipants(entry) {
    const receipt = receiptForEntry(entry);
    if (!receipt) {
      setMessage("Não encontrei o recebimento relacionado a este lançamento.");
      return;
    }

    setEditingEntry(null);
    setEditingReceiptEntryId(entry.id);
    setReceiptParticipants((current) => ({
      ...current,
      [receipt.id]: participantStateForReceipt(receipt),
    }));
  }

  async function removeReceiptParticipant(entry) {
    const receipt = receiptForEntry(entry);
    if (!receipt) {
      setMessage("Não encontrei o recebimento relacionado a este lançamento.");
      return;
    }

    const selectedIds = receiptParticipantIds(receipt).filter((id) => id !== Number(entry.funcionario_id));
    if (!selectedIds.length) {
      setMessage("O recebimento precisa ficar com ao menos um participante.");
      return;
    }

    if (!confirm("Remover este participante do recebimento?")) return;

    setReceiptParticipants((current) => ({
      ...current,
      [receipt.id]: Object.fromEntries(selectedIds.map((id) => [id, true])),
    }));

    setMessage("");
    try {
      const saved = await api.put(`/recebimentos-toneladas/${receipt.id}/participantes`, {
        funcionario_ids: selectedIds,
        usuario_lancamento: loggedUser || null,
      });
      await load();
      setMessage(`Participante removido. Recebimento agora tem ${saved.length} participante(s).`);
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
    const editingIsEvaluation = normalizeText(editingEntry.tipo_lancamento) === "avaliacao_semanal";
    const adjustments = normalizedCustomAdjustments(editingEntry);
    const firstAdjustment = adjustments[0] || {};

    try {
      await api.put(`/lancamentos-semanais/${editingEntry.id}`, {
        semana: editingEntry.semana,
        data_lancamento: editingEntry.data_lancamento,
        pedidos_separados: editingIsEvaluation ? 0 : criterionValue(editingEntry, "pedidos_separados"),
        pedidos_carregados: editingIsEvaluation ? 0 : criterionValue(editingEntry, "pedidos_carregados"),
        toneladas: editingIsEvaluation ? 0 : criterionValue(editingEntry, "toneladas", editingEmployeeIsDelivery && !isCriterionAdded(editingEntry, "toneladas")),
        numero_carregamento: editingIsEvaluation ? null : editingEntry.numero_carregamento || null,
        numero_nota_fiscal: !editingIsEvaluation && editingEmployeeReceivesTonnes ? editingEntry.numero_nota_fiscal || null : null,
        nota_fiscal_pdf: !editingIsEvaluation && editingEmployeeReceivesTonnes ? editingEntry.nota_fiscal_pdf || null : null,
        nota_fiscal_pdf_nome: !editingIsEvaluation && editingEmployeeReceivesTonnes ? editingEntry.nota_fiscal_pdf_nome || null : null,
        entregas: editingIsEvaluation ? 0 : criterionValue(editingEntry, "entregas"),
        retornos: editingIsEvaluation ? 0 : criterionValue(editingEntry, "retornos"),
        nota: editingIsEvaluation ? Number(editingEntry.nota) : 5,
        penalidade: editingIsEvaluation ? false : Boolean(editingEntry.penalidade),
        motivo_penalidade: !editingIsEvaluation && editingEntry.penalidade
        ? editingEntry.motivo_penalidade
        : null,
        ajuste_personalizado_descricao: editingIsEvaluation ? null : firstAdjustment.criterio || null,
        ajuste_personalizado_operacao: editingIsEvaluation ? null : firstAdjustment.operacao || null,
        ajuste_personalizado_valor: !editingIsEvaluation && firstAdjustment.criterio ? criterionValue(editingEntry, firstAdjustment.criterio) : 0,
        ajuste_personalizado_itens: !editingIsEvaluation && adjustments.length ? JSON.stringify(adjustments) : null,
      });

      setEditingEntry(null);
      await load();
      setMessage("Lançamento atualizado.")
    } catch (err){
      setMessage(errorMessage(err));
    }
}

  function renderReceiptParticipantEditForm(entry) {
    const receipt = receiptForEntry(entry);
    if (!receipt) return null;

    return (
      <form
        className="inline-edit-form receipt-participant-edit-form"
        onSubmit={async (event) => {
          event.preventDefault();
          await saveReceiptParticipants(receipt.id);
        }}
      >
        <h2>Editar participantes</h2>

        <div className="participant-grid">
          {receiptVisibleEmployees(receipt).map((employee) => (
            <label className="check" key={employee.id}>
              <input
                checked={Boolean(receiptParticipants[receipt.id]?.[employee.id])}
                type="checkbox"
                onChange={(event) => toggleReceiptParticipant(receipt.id, employee.id, event.target.checked)}
              />
              {employee.nome}
              {!isMorningEmployee(employee) && <small>{employee.turno}</small>}
            </label>
          ))}
        </div>

        <div className="receipt-participant-actions">
          <label>
            Adicionar funcionário
            <select
              value={receiptExtraEmployeeId[receipt.id] || ""}
              onChange={(event) =>
                setReceiptExtraEmployeeId((current) => ({
                  ...current,
                  [receipt.id]: event.target.value,
                }))
              }
            >
              <option value="">Selecione</option>
              {receiptExtraEmployeeOptions(receipt).map((employee) => (
                <option key={employee.id} value={employee.id}>
                  {employee.nome} - {employee.turno || "Sem turno"}
                </option>
              ))}
            </select>
          </label>

          <button onClick={() => addReceiptExtraEmployee(receipt.id)} type="button">
            <Plus size={17} /> Adicionar
          </button>
          <button className="primary" type="submit"><Save size={17} /> Salvar participantes</button>
          <button className="icon-button" onClick={() => setEditingReceiptEntryId(null)} type="button">X</button>
        </div>
      </form>
    );
  }

  function renderReceiptEditForm() {
    if (!editingReceipt) return null;

    return (
      <form className="inline-edit-form receipt-edit-form" onSubmit={updateReceipt}>
        <h2>Editar recebimento</h2>

        <input
          value={editingReceipt.semana}
          onChange={(event) => setEditingReceipt({ ...editingReceipt, semana: event.target.value })}
          required
        />
        <input
          type="date"
          value={editingReceipt.data_lancamento || ""}
          onChange={(event) => setEditingReceipt({ ...editingReceipt, data_lancamento: event.target.value })}
        />
        <input
          min="0"
          step="0.1"
          type="number"
          placeholder="Toneladas"
          value={editingReceipt.toneladas || ""}
          onChange={(event) => setEditingReceipt({ ...editingReceipt, toneladas: event.target.value })}
          required
        />
        <input
          placeholder="N° carregamento"
          value={editingReceipt.numero_carregamento || ""}
          onChange={(event) => setEditingReceipt({ ...editingReceipt, numero_carregamento: event.target.value })}
        />
        <input
          placeholder="Número da nota fiscal"
          value={editingReceipt.numero_nota_fiscal || ""}
          onChange={(event) => setEditingReceipt({ ...editingReceipt, numero_nota_fiscal: event.target.value })}
        />
        <label>
          PDF da nota fiscal (opcional)
          <input
            accept="application/pdf,.pdf"
            type="file"
            onChange={(event) => selectInvoicePdf(event.target.files?.[0], setEditingReceipt)}
          />
        </label>
        {editingReceipt.nota_fiscal_pdf_disponivel && !editingReceipt.nota_fiscal_pdf && (
          <a href={downloadUrl(`/recebimentos-toneladas/${editingReceipt.id}/nota-fiscal`)} rel="noreferrer" target="_blank">
            Abrir PDF atual
          </a>
        )}

        <div className="entry-edit-actions">
          <button className="primary" type="submit"><Save size={17} /> Salvar alterações</button>
          <button className="icon-button" onClick={() => setEditingReceipt(null)} type="button">X</button>
        </div>
      </form>
    );
  }

  function renderEntryEditForm() {
    if (!editingEntry) return null;
    const editingIsEvaluation = normalizeText(editingEntry.tipo_lancamento) === "avaliacao_semanal";

    return (
      <form className="inline-edit-form entry-edit-form" onSubmit={updateEntry}>
        <h2>Editar lançamento</h2>

        <div className="entry-edit-main-fields">
          <input value={editingEntry.semana} onChange={(event) => setEditingEntry({ ...editingEntry, semana: event.target.value })} required />
          <input type="date" value={editingEntry.data_lancamento || ""} onChange={(event) => setEditingEntry({ ...editingEntry, data_lancamento: event.target.value })} />

          {!editingIsEvaluation && bonusCriteria.map((criterion) => (
            shouldShowCriterion(editingEntry, editingEmployeeTurn, editingEmployeeIsDelivery, criterion.id) && (
              <input
                key={criterion.id}
                min="0"
                step={criterion.step}
                type={criterion.type}
                placeholder={criterion.label}
                value={metricInputValue(editingEntry, criterion.id)}
                onChange={(event) => updateMetric(editingEntry, setEditingEntry, criterion.id, event.target.value)}
              />
            )
          ))}

          {!editingIsEvaluation && (
          <input
            placeholder="N° carregamento"
            value={editingEntry.numero_carregamento || ""}
            onChange={(event) => setEditingEntry({ ...editingEntry, numero_carregamento: event.target.value })}
          />
          )}
        </div>

        {!editingIsEvaluation && editingEmployeeReceivesTonnes && (
          <div className="entry-edit-invoice-fields">
            <input
              placeholder="Número da nota fiscal"
              value={editingEntry.numero_nota_fiscal || ""}
              onChange={(event) => setEditingEntry({ ...editingEntry, numero_nota_fiscal: event.target.value })}
            />
            <label>
              PDF da nota fiscal (opcional)
              <input
                accept="application/pdf,.pdf"
                type="file"
                onChange={(event) => selectInvoicePdf(event.target.files?.[0], setEditingEntry)}
              />
            </label>
            {editingEntry.nota_fiscal_pdf_disponivel && !editingEntry.nota_fiscal_pdf && (
              <a href={downloadUrl(`/lancamentos-semanais/${editingEntry.id}/nota-fiscal`)} rel="noreferrer" target="_blank">
                Abrir PDF atual
              </a>
            )}
          </div>
        )}

        {editingIsEvaluation && (
        <select value={editingEntry.nota} onChange={(event) => setEditingEntry({ ...editingEntry, nota: event.target.value })}>
          {[1, 2, 3, 4, 5].map((note) => <option key={note}>{note}</option>)}
        </select>
        )}

        {!editingIsEvaluation && (
        <div className="entry-edit-penalty-fields">
          <label className="check">
            <input checked={editingEntry.penalidade} type="checkbox" onChange={(event) => setEditingEntry({ ...editingEntry, penalidade: event.target.checked })} />
            Penalidade
          </label>

          {editingEntry.penalidade && (
            <input placeholder="Motivo" value={editingEntry.motivo_penalidade || ""} onChange={(event) => setEditingEntry({ ...editingEntry, motivo_penalidade: event.target.value })} required />
          )}
        </div>
        )}

        {!editingIsEvaluation && (
        <div className="custom-adjustment-fields">
          {customAdjustments(editingEntry).map((adjustment, index) => (
            <Fragment key={`${adjustment.criterio}-${index}`}>
              <select value={adjustment.criterio} onChange={(event) => updateCustomAdjustment(editingEntry, setEditingEntry, index, "criterio", event.target.value)}>
                {bonusCriteria.map((criterion) => <option key={criterion.id} value={criterion.id}>{criterion.label}</option>)}
              </select>
              <select value={adjustment.operacao} onChange={(event) => updateCustomAdjustment(editingEntry, setEditingEntry, index, "operacao", event.target.value)}>
                <option value="adicionar">Adicionar</option>
                <option value="retirar">Retirar</option>
              </select>
              <button className="icon-button danger" onClick={() => removeCustomAdjustment(editingEntry, setEditingEntry, index)} title="Remover critério" type="button">
                <Trash2 size={16} />
              </button>
            </Fragment>
          ))}
          <button className="primary wide-button" onClick={() => addCustomAdjustment(editingEntry, setEditingEntry)} type="button">
            <Plus size={17} /> Adicionar critério
          </button>
        </div>
        )}

        <div className="entry-edit-actions">
          <button className="primary" type="submit"><Save size={17} /> Salvar alterações</button>
          <button className="icon-button" onClick={() => setEditingEntry(null)} type="button">X</button>
        </div>
      </form>
    );
  }

  return (
    <section className="view">
      {showForm && (
        <>
          {canManageEntries && (
          <>
          <div className="panel form-grid">
            <h2>Novo lançamento</h2>
            <select value={form.tipo_lancamento} onChange={(event) => changeEntryType(event.target.value)}>
              <option value="semanal">Semanal</option>
              <option value="diario">Diário</option>
              <option value="mensal">Mensal</option>
              {canCreateSupervisorEntries && <option value="recebimento_toneladas">Recebimento de toneladas</option>}
              {canCreateSupervisorEntries && <option value="avaliacao_semanal">Avaliação semanal</option>}
            </select>
          </div>

          {form.tipo_lancamento !== "mensal" && (
            <form className="panel form-grid entries-form" onSubmit={saveEntry}>
          <div className="entry-form-title">
            <h2>{entryTypeLabel(form.tipo_lancamento)}</h2>
            {!isReceiptEntry && !isEvaluationEntry && (
            <div className={`entry-actions ${entryMenuOpen ? "open" : ""}`}>
              <button
                className="icon-button"
                onClick={() => setEntryMenuOpen((open) => !open)}
                title="Mais opções"
                type="button"
              >
                <MoreVertical size={16} />
              </button>
              {entryMenuOpen && (
                <div className="entry-actions-menu">
                  <button
                    type="button"
                    onClick={() => {
                      setCustomEntryEnabled((enabled) => {
                        if (!enabled && !customAdjustments(form).length) {
                          setForm({
                            ...form,
                            ajustes_personalizados: [{ criterio: "pedidos_separados", operacao: "adicionar" }],
                          });
                        }
                        return !enabled;
                      });
                      setEntryMenuOpen(false);
                    }}
                  >
                    Lançamento personalizado
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setInvoiceFieldsEnabled((enabled) => {
                        const next = !enabled;
                        if (!next) {
                          setForm((current) => ({
                            ...current,
                            numero_nota_fiscal: "",
                            nota_fiscal_pdf: null,
                            nota_fiscal_pdf_nome: null,
                          }));
                        }
                        return next;
                      });
                      setEntryMenuOpen(false);
                    }}
                  >
                    {invoiceFieldsEnabled ? "Remover NF" : "Adicionar NF"}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setLoadingNumberFieldsEnabled((enabled) => {
                        const next = !enabled;
                        if (!next) {
                          setForm((current) => ({
                            ...current,
                            numero_carregamento: "",
                          }));
                        }
                        return next;
                      });
                      setEntryMenuOpen(false);
                    }}
                  >
                    {loadingNumberFieldsEnabled ? "Remover N° carregamento" : "Adicionar N° carregamento"}
                  </button>
                </div>
              )}
            </div>
            )}
          </div>
          {!isReceiptEntry && (
          <select
            value={form.funcionario_id}
            onChange={(event) => {
              setForm({
                ...form,
                funcionario_id: event.target.value,
                pedidos_separados: 0,
                pedidos_carregados: 0,
                toneladas: 0,
                entregas: 0,
                retornos: 0,
                numero_carregamento: "",
                numero_nota_fiscal: "",
                nota_fiscal_pdf: null,
                nota_fiscal_pdf_nome: null,
              });
              setLoadingNumberFieldsEnabled(false);
              setInvoiceFieldsEnabled(false);
            }}
            required
          >
            <option value="">Funcionário</option>
            {availableEntryEmployees.map((employee) => (
              <option key={employee.id} value={employee.id}>{employeeLabel(employee)}</option>
            ))}
          </select>
          )}
          <input type="date" value={form.data_lancamento} onChange={(event) => setForm({ ...form, data_lancamento: event.target.value })} />
          {!isEvaluationEntry && bonusCriteria.map((criterion) => (
            shouldShowCriterion(customEntryEnabled ? form : withoutCustomAdjustments(form), selectedEmployeeTurn, selectedEmployeeIsDelivery, criterion.id) && (
              <input
                key={criterion.id}
                min="0"
                step={criterion.step}
                type={criterion.type}
                placeholder={criterion.label}
                value={form[criterion.id]}
                onChange={(event) => updateMetric(form, setForm, criterion.id, event.target.value)}
              />
            )
          ))}
          {isReceiptEntry && (
            <input
              min="0"
              step="0.1"
              type="number"
              placeholder="Toneladas recebidas"
              value={form.toneladas}
              onChange={(event) => setForm({ ...form, toneladas: event.target.value })}
              required
            />
          )}
          {isReceiptEntry && (
            <input
              placeholder="N° carregamento"
              value={form.numero_carregamento}
              onChange={(event) => setForm({ ...form, numero_carregamento: event.target.value })}
            />
          )}
          {isReceiptEntry && (
            <>
              <input
                placeholder="Número da nota fiscal"
                value={form.numero_nota_fiscal}
                onChange={(event) => setForm({ ...form, numero_nota_fiscal: event.target.value })}
              />
              <label>
                PDF da nota fiscal (opcional)
                <input
                  accept="application/pdf,.pdf"
                  type="file"
                  onChange={(event) => selectInvoicePdf(event.target.files?.[0], setForm)}
                />
              </label>
            </>
          )}
          {showLoadingNumberFields && (
            <input
              placeholder="N° carregamento"
              value={form.numero_carregamento}
              onChange={(event) => setForm({ ...form, numero_carregamento: event.target.value })}
            />
          )}
          {showInvoiceFields && (
            <>
              <input
                placeholder="Número da nota fiscal"
                value={form.numero_nota_fiscal}
                onChange={(event) => setForm({ ...form, numero_nota_fiscal: event.target.value })}
              />
              <label>
                PDF da nota fiscal (opcional)
                <input
                  accept="application/pdf,.pdf"
                  type="file"
                  onChange={(event) => selectInvoicePdf(event.target.files?.[0], setForm)}
                />
              </label>
            </>
          )}
          {isEvaluationEntry && (
          <select value={form.nota} onChange={(event) => setForm({ ...form, nota: event.target.value })}>
            {[1, 2, 3, 4, 5].map((note) => <option key={note}>{note}</option>)}
          </select>
          )}
          {!isEvaluationEntry && !isReceiptEntry && (
          <label className="check">
            <input checked={form.penalidade} type="checkbox" onChange={(event) => setForm({ ...form, penalidade: event.target.checked })} />
            Penalidade
          </label>
          )}
          {form.penalidade && <input placeholder="Motivo" value={form.motivo_penalidade} onChange={(event) => setForm({ ...form, motivo_penalidade: event.target.value })} required />}
          {customEntryEnabled && !isEvaluationEntry && !isReceiptEntry && (
            <div className="custom-adjustment-fields">
              {customAdjustments(form).map((adjustment, index) => (
                <Fragment key={`${adjustment.criterio}-${index}`}>
                  <select
                    value={adjustment.criterio}
                    onChange={(event) => updateCustomAdjustment(form, setForm, index, "criterio", event.target.value)}
                    required
                  >
                    {bonusCriteria.map((criterion) => <option key={criterion.id} value={criterion.id}>{criterion.label}</option>)}
                  </select>
                  <select value={adjustment.operacao} onChange={(event) => updateCustomAdjustment(form, setForm, index, "operacao", event.target.value)}>
                    <option value="adicionar">Adicionar</option>
                    <option value="retirar">Retirar</option>
                  </select>
                  <button className="icon-button danger" onClick={() => removeCustomAdjustment(form, setForm, index)} title="Remover critério" type="button">
                    <Trash2 size={16} />
                  </button>
                </Fragment>
              ))}
              <button className="primary wide-button" onClick={() => addCustomAdjustment(form, setForm)} type="button">
                <Plus size={17} /> Adicionar critério
              </button>
            </div>
          )}
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
              setMonthlyForm({
                ...monthlyForm,
                filtro_turno: event.target.value,
                pedidos_separados: 0,
                pedidos_carregados: 0,
                toneladas: 0,
                entregas: 0,
                retornos: 0,
                notas: {},
              })
            }
          >
            <option value="Manhã">Manhã</option>
            <option value="Tarde">Tarde</option>
            <option value="Noite">Noite</option>
            <option value="Horário comercial">Horário comercial</option>
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

          {monthlyIsDelivery && !monthlyIsCommercialHours && (
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
            <table className="monthly-table">
              <thead>
                <tr><th>Funcionário</th><th>Cargo</th><th>Turno</th><th>Nota</th></tr>
              </thead>
              <tbody>
                {monthlyEmployees.map((employee) => (
                  <tr key={employee.id}>
                    <td data-label="Funcionário">{employee.nome}</td>
                    <td data-label="Cargo">{employee.cargo}</td>
                    <td data-label="Turno">{employee.turno}</td>
                    <td data-label="Nota">
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

          {canViewPendingReceipts && (
            <section className="panel receipt-panel">
              <div className="section-heading">
                <div>
                  <h2>Recebimentos pendentes</h2>
                  <p>{pendingReceipts.length} lançamento(s) aguardando participantes</p>
                </div>
              </div>

              {!pendingReceipts.length && <div className="alert">Nenhum recebimento pendente.</div>}

              {pendingReceipts.map((receipt) => (
                <div className="receipt-card" key={receipt.id}>
                  <div className="receipt-card-header">
                    <div>
                      <strong>{Number(receipt.toneladas || 0).toLocaleString("pt-BR")} toneladas</strong>
                      <span>{receipt.semana} · {receipt.data_lancamento || "-"} · Supervisor: {receipt.usuario_lancamento || "-"}</span>
                      <small>NF {receipt.numero_nota_fiscal || "-"} · Carregamento {receipt.numero_carregamento || "-"}</small>
                    </div>

                    <div className="receipt-card-actions">
                      {!canChooseReceiptParticipants && (
                        <>
                          <button
                            className="icon-button"
                            onClick={() => {
                              setEditingReceipt((current) => current?.id === receipt.id ? null : { ...receipt });
                              setReceiptMenuOpen(null);
                            }}
                            title="Editar recebimento"
                            type="button"
                          >
                            <Pencil size={16} />
                          </button>
                          <button
                            className="icon-button danger"
                            onClick={() => removeReceipt(receipt.id)}
                            title="Excluir recebimento"
                            type="button"
                          >
                            <Trash2 size={16} />
                          </button>
                        </>
                      )}

                      {canChooseReceiptParticipants && (
                        <div className={`entry-actions ${receiptMenuOpen === receipt.id ? "open" : ""}`}>
                          <button
                            className="icon-button"
                            onClick={() => setReceiptMenuOpen((current) => (current === receipt.id ? null : receipt.id))}
                            title="Mais opções"
                            type="button"
                          >
                            <MoreVertical size={16} />
                          </button>
                          {receiptMenuOpen === receipt.id && (
                            <div className="entry-actions-menu receipt-actions-menu">
                              <label>
                                Adicionar funcionário
                                <select
                                  value={receiptExtraEmployeeId[receipt.id] || ""}
                                  onChange={(event) =>
                                    setReceiptExtraEmployeeId((current) => ({
                                      ...current,
                                      [receipt.id]: event.target.value,
                                    }))
                                  }
                                >
                                  <option value="">Selecione</option>
                                  {receiptExtraEmployeeOptions(receipt).map((employee) => (
                                    <option key={employee.id} value={employee.id}>
                                      {employee.nome} - {employee.turno || "Sem turno"}
                                    </option>
                                  ))}
                                </select>
                              </label>
                              <button onClick={() => addReceiptExtraEmployee(receipt.id)} type="button">
                                Adicionar
                              </button>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>

                  {editingReceipt?.id === receipt.id && renderReceiptEditForm()}

                  {canChooseReceiptParticipants && (
                    <>
                      <div className="participant-grid">
                        {receiptVisibleEmployees(receipt).map((employee) => (
                          <label className="check" key={employee.id}>
                            <input
                              checked={Boolean(receiptParticipants[receipt.id]?.[employee.id])}
                              type="checkbox"
                              onChange={(event) => toggleReceiptParticipant(receipt.id, employee.id, event.target.checked)}
                            />
                            {employee.nome}
                            {!isMorningEmployee(employee) && <small>{employee.turno}</small>}
                          </label>
                        ))}
                      </div>

                      <button className="primary" onClick={() => saveReceiptParticipants(receipt.id)} type="button">
                        <Save size={17} /> Confirmar participantes
                      </button>
                    </>
                  )}
                </div>
              ))}
            </section>
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
                <option value="recebimento_toneladas">Recebimento toneladas</option>
                <option value="avaliacao_semanal">Avaliação semanal</option>
              </select>
            </label>

            <label>
              Turno
              <select value={turnFilter} onChange={(event) => setTurnFilter(event.target.value)}>
                <option>Todos</option>
                <option>Manhã</option>
                <option>Tarde</option>
                <option>Noite</option>
                <option>Horário comercial</option>
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
            <table className="history-table">
              <thead>
                <tr><th>ID</th><th>Funcionário</th><th>Tipo</th><th>Semana</th><th>Lançou</th><th>Escolheu</th><th>Nota</th><th>N° carregamento</th><th>Nota fiscal</th><th>Ajuste</th><th>Bônus</th><th></th></tr>
              </thead>
              <tbody>
                {filteredEntries.map((entry) => {
                  const userInfo = entryUserInfo(entry);
                  return (
                  <Fragment key={entry.id}>
                    <tr>
                      <td data-label="ID">{entry.id}</td>
                      <td data-label="Funcionário">{employeeMap[entry.funcionario_id]?.nome || `#${entry.funcionario_id}`}</td>
                      <td data-label="Tipo">{entryTypeLabel(entry.tipo_lancamento)}</td>
                      <td data-label="Semana">{entry.semana}</td>
                      <td data-label="Lançou">{userInfo.launchedBy}</td>
                      <td data-label="Escolheu">{userInfo.chosenBy}</td>
                      <td data-label="Nota">{normalizeText(entry.tipo_lancamento) === "avaliacao_semanal" ? entry.nota : "-"}</td>
                      <td data-label="N° carregamento">{entry.numero_carregamento || "-"}</td>
                      <td data-label="Nota fiscal">{entry.numero_nota_fiscal || "-"}</td>
                      <td className="adjustment-cell" data-label="Ajuste" title={customAdjustmentSummary(entry)}>
                        {customAdjustmentSummary(entry)}
                      </td>
                      <td className="bonus-cell" data-label="Bônus">{currency.format(Number(entry.bonus_calculado || 0))}</td>
                      <td className="row-actions" data-label="Ações">
                        {entry.nota_fiscal_pdf_disponivel && (
                          <a
                            className="icon-button pdf-button"
                            href={downloadUrl(`/lancamentos-semanais/${entry.id}/nota-fiscal`)}
                            rel="noreferrer"
                            target="_blank"
                            title={`Abrir nota fiscal ${entry.numero_nota_fiscal || ""}`.trim()}
                          >
                            PDF
                          </a>
                        )}
                        {(canManageEntries || (canChooseReceiptParticipants && normalizeText(entry.tipo_lancamento) === "recebimento_toneladas")) && (
                          <>
                            <button
                              className="icon-button"
                              onClick={() => {
                                if (canManageEntries) {
                                  setEditingReceiptEntryId(null);
                                  setEditingEntry({
                                    ...entry,
                                    ajustes_personalizados: customAdjustments(entry),
                                  });
                                  return;
                                }

                                editReceiptParticipants(entry);
                              }}
                              title={canManageEntries ? "Editar lançamento" : "Editar participantes"}
                              type="button"
                            >
                              <Pencil size={16} />
                            </button>

                            <button
                              className="icon-button danger"
                              onClick={() => {
                                if (canManageEntries) {
                                  removeEntry(entry.id);
                                  return;
                                }

                                removeReceiptParticipant(entry);
                              }}
                              title={canManageEntries ? "Excluir lançamento" : "Remover participante"}
                              type="button"
                            >
                              <Trash2 size={16} />
                            </button>
                          </>
                        )}
                      </td>
                    </tr>

                    {editingEntry?.id === entry.id && (
                      <tr className="inline-edit-row">
                        <td colSpan="12">{renderEntryEditForm()}</td>
                      </tr>
                    )}

                    {editingReceiptEntryId === entry.id && (
                      <tr className="inline-edit-row">
                        <td colSpan="12">{renderReceiptParticipantEditForm(entry)}</td>
                      </tr>
                    )}
                  </Fragment>
                  );
                })}
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
  const activeEmployees = employees.filter((employee) => employee.ativo);
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
          {activeEmployees.map((employee) => <option key={employee.id} value={employee.id}>{employeeLabel(employee)}</option>)}
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
          {activeEmployees.map((employee) => <option key={employee.id} value={employee.id}>{employeeLabel(employee)}</option>)}
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
        <table className="frequency-table">
          <thead>
            <tr><th>ID</th><th>Funcionário</th><th>Mês</th><th>Status</th><th>Ausências</th><th>Dia</th><th>Tipo</th><th></th></tr>
          </thead>
          <tbody>
            {frequencies.map((frequency) => (
              <Fragment key={frequency.id}>
                <tr>
                  <td data-label="ID">{frequency.id}</td>
                  <td data-label="Funcionário">{employeeMap[frequency.funcionario_id]?.nome || `#${frequency.funcionario_id}`}</td>
                  <td data-label="Mês">{frequency.mes}</td>
                  <td data-label="Status">{frequency.status_mes}</td>
                  <td data-label="Ausências">{frequency.ausencias}</td>
                  <td data-label="Dia">{frequency.data_falta || "-"}</td>
                  <td data-label="Tipo">{frequency.tipo_falta || "-"}</td>
                  <td className="row-actions" data-label="Ações">
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
  const [selectedMonth, setSelectedMonth] = useState(month);
  const [closing, setClosing] = useState([]);
  const [message, setMessage] = useState("");
  const [editingDiscount, setEditingDiscount] = useState(null);

  async function calculate() {
    setMessage("");
    if (!isValidMonthInput(selectedMonth)) return;

    try {
      const data = await api.get(`/fechamento/${selectedMonth}`);
      setClosing(Array.isArray(data) ? data : []);
      setEditingDiscount(null);
    } catch (err) {
      setMessage(errorMessage(err));
    }
  }

  function changeClosingMonth(value) {
    setMonth(value);
    if (isValidMonthInput(value)) {
      setSelectedMonth(value);
    }
  }

  function startDiscount(item) {
    setMessage("");
    setEditingDiscount({
      funcionario_id: item.funcionario_id,
      funcionario: item.funcionario,
      valor: Number(item.desconto || 0) || "",
      motivo: item.motivo_desconto || "",
    });
  }

  async function saveDiscount(event) {
    event.preventDefault();
    setMessage("");

    try {
      await api.post("/descontos-fechamento", {
        funcionario_id: editingDiscount.funcionario_id,
        mes: selectedMonth,
        valor: Number(editingDiscount.valor || 0),
        motivo: editingDiscount.motivo,
      });
      await calculate();
      setMessage("Desconto aplicado.");
    } catch (err) {
      setMessage(errorMessage(err));
    }
  }

  async function removeDiscount() {
    if (!editingDiscount) return;
    setMessage("");

    try {
      await api.delete(`/descontos-fechamento/${selectedMonth}/${editingDiscount.funcionario_id}`);
      await calculate();
      setMessage("Desconto removido.");
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
          <input type="month" value={month} onChange={(event) => changeClosingMonth(event.target.value)} />
        </label>
        <button className="primary" onClick={calculate} type="button"><BarChart3 size={17} /> Calcular</button>
        <a className="button-link" href={downloadUrl(`/exportar-fechamento/${selectedMonth}`)}>
          <FileSpreadsheet size={17} /> Excel
        </a>
      </div>

      {message && <div className="alert error">{message}</div>}

      <div className="table-wrap closing-table-wrap">
        <table className="closing-table">
          <thead>
            <tr><th>Funcionário</th><th>Cargo</th><th>Status</th><th>Nota atual</th><th>Ausências</th><th>Lançamentos</th><th>Assiduidade</th><th>Desconto</th><th>Bônus final</th><th></th></tr>
          </thead>
          <tbody>
            {closing.map((item) => (
              <Fragment key={item.funcionario_id}>
                <tr>
                  <td data-label="Funcionário">{item.funcionario}</td>
                  <td data-label="Cargo">{item.cargo}</td>
                  <td data-label="Status"><span className={item.elegivel ? "badge ok" : "badge danger"}>{item.status_mes === "Férias" ? "Férias" : item.elegivel ? "Elegível" : "Bloqueado"}</span></td>
                  <td data-label="Nota atual">{item.nota_atual ?? "-"}</td>
                  <td data-label="Ausências">{item.ausencias}</td>
                  <td data-label="Lançamentos">{item.quantidade_lancamentos}</td>
                  <td data-label="Assiduidade">{currency.format(Number(item.assiduidade || 0))}</td>
                  <td data-label="Desconto" title={item.motivo_desconto || ""}>{currency.format(Number(item.desconto || 0))}</td>
                  <td data-label="Bônus final">
                    <strong>{currency.format(Number(item.bonus_final || 0))}</strong>
                    {Number(item.desconto || 0) > 0 && (
                      <small className="bonus-before-discount">
                        de {currency.format(Number(item.bonus_bruto || 0))}
                      </small>
                    )}
                  </td>
                  <td className="row-actions" data-label="Ações">
                    <button
                      className="icon-button"
                      onClick={() => startDiscount(item)}
                      title="Aplicar desconto"
                      type="button"
                    >
                      <CircleMinus size={16} />
                    </button>
                  </td>
                </tr>

                {editingDiscount?.funcionario_id === item.funcionario_id && (
                  <tr className="inline-edit-row">
                    <td colSpan="10">
                      <form className="inline-edit-form discount-form" onSubmit={saveDiscount}>
                        <h2>Desconto de {editingDiscount.funcionario}</h2>
                        <label>
                          Valor
                          <input
                            min="0"
                            step="0.01"
                            type="number"
                            value={editingDiscount.valor}
                            onChange={(event) => setEditingDiscount({ ...editingDiscount, valor: event.target.value })}
                          />
                        </label>
                        <label>
                          Motivo
                          <input
                            placeholder="Opcional"
                            value={editingDiscount.motivo}
                            onChange={(event) => setEditingDiscount({ ...editingDiscount, motivo: event.target.value })}
                          />
                        </label>
                        <button className="primary" type="submit"><Save size={17} /> Salvar desconto</button>
                        <button className="icon-button danger" onClick={removeDiscount} title="Remover desconto" type="button">
                          <Trash2 size={16} />
                        </button>
                        <button className="icon-button" onClick={() => setEditingDiscount(null)} type="button">X</button>
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

function Rules() {
  const rules = [
    {
      title: "Assiduidade mensal",
      icon: CalendarCheck,
      text: "Todo funcionário inicia o mês com o valor de assiduidade. Qualquer ausência registrada no mês remove esse valor.",
      values: ["R$ 150,00 por mês", "Perde com 1 ausência"],
    },
    {
      title: "Regra por turno",
      icon: Clock,
      text: "A base de cálculo muda conforme o turno cadastrado para o funcionário.",
      values: ["Manhã: R$ 2,00 por tonelada", "Tarde: R$ 0,10 por pedido separado", "Noite: R$ 0,10 por pedido carregado", "Horário comercial: apenas assiduidade"],
    },
    {
      title: "Funcionários de entrega",
      icon: Truck,
      text: "Motoristas e ajudantes entram no mesmo grupo operacional para os lançamentos de entrega. Cada entrega aumenta o bônus e cada retorno desconta do valor.",
      values: ["Motorista = Entrega", "Ajudante = Entrega", "+ R$ 0,30 por entrega", "- R$ 0,60 por retorno"],
    },
    {
      title: "Nota de desempenho",
      icon: Star,
      text: "A nota atual aplica um multiplicador sobre a bonificação calculada no período.",
      values: ["5: 100%", "4: 90%", "3: 80%", "2: 50%", "1: 20%"],
    },
    {
      title: "Penalidade",
      icon: Percent,
      text: "Quando marcada no lançamento, a bonificação é reduzida pela metade e o motivo precisa ficar registrado.",
      values: ["Redução de 50%", "Motivo obrigatório"],
    },
  ];

  return (
    <section className="view">
      <div className="panel rules-panel">
        <div className="rules-heading">
          <div>
            <h2>Regras de Negócio</h2>
            <p>Resumo dos critérios usados no cálculo da bonificação.</p>
          </div>
          <span>5 regras</span>
        </div>

        <div className="rules-list">
          {rules.map(({ title, icon: Icon, text, values }) => (
            <article className="rule-item" key={title}>
              <div className="rule-icon" aria-hidden="true">
                <Icon size={21} />
              </div>

              <div className="rule-content">
                <h3>{title}</h3>
                <p>{text}</p>

                <div className="rule-values">
                  {values.map((value) => (
                    <span key={value}>{value}</span>
                  ))}
                </div>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
