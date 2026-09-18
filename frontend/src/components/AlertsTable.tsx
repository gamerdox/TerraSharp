import React, { useState, useEffect } from "react";
import {
  AlertItem,
  VillageRiskSummary,
  AlertTransitionItem,
  EmailDispatchRecord,
  AlertState,
} from "../types";
import {
  ShieldAlert,
  AlertTriangle,
  CheckCircle,
  Search,
  Mail,
  History,
  Send,
  RefreshCw,
  Clock,
  ExternalLink,
  ChevronRight,
  Activity,
  Check,
  X,
  Loader2,
} from "lucide-react";
import { fetchAlertHistory, fetchEmailLogs, sendTestEmail } from "../api";

interface AlertsTableProps {
  alerts: AlertItem[];
  villages: VillageRiskSummary[];
  onSelectVillage: (village: VillageRiskSummary) => void;
  selectedVillageId?: string;
}

type TabType = "ACTIVE" | "HISTORY" | "EMAILS";

export const AlertsTable: React.FC<AlertsTableProps> = ({
  alerts,
  villages,
  onSelectVillage,
  selectedVillageId,
}) => {
  const [activeTab, setActiveTab] = useState<TabType>("ACTIVE");
  const [filter, setFilter] = useState<string>("ALL");
  const [search, setSearch] = useState<string>("");

  // History & Email logs state
  const [historyItems, setHistoryItems] = useState<AlertTransitionItem[]>([]);
  const [emailLogs, setEmailLogs] = useState<EmailDispatchRecord[]>([]);
  const [loadingExtras, setLoadingExtras] = useState<boolean>(false);

  // Test Email Modal / Form state
  const [showTestModal, setShowTestModal] = useState<boolean>(false);
  const [testEmailInput, setTestEmailInput] = useState<string>("");
  const [testSeverity, setTestSeverity] = useState<AlertState>("WARNING");
  const [testVillageName, setTestVillageName] = useState<string>("Wayanad Sector 4");
  const [sendingTest, setSendingTest] = useState<boolean>(false);
  const [testResultMsg, setTestResultMsg] = useState<{ text: string; success: boolean } | null>(null);

  // Load history and email records on tab switch or periodically
  const loadExtras = async () => {
    try {
      setLoadingExtras(true);
      const [hist, emails] = await Promise.all([
        fetchAlertHistory(50).catch(() => []),
        fetchEmailLogs(50).catch(() => []),
      ]);
      setHistoryItems(hist);
      setEmailLogs(emails);
    } finally {
      setLoadingExtras(false);
    }
  };

  useEffect(() => {
    loadExtras();
  }, [activeTab]);

  const handleSendTestEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    setSendingTest(true);
    setTestResultMsg(null);
    try {
      const res = await sendTestEmail({
        recipient_email: testEmailInput.trim() || undefined,
        severity: testSeverity,
        village_name: testVillageName.trim() || "Wayanad Sector 4",
      });
      setTestResultMsg({
        text: res.message,
        success: res.status === "SENT" || res.status === "SIMULATED",
      });
      loadExtras();
    } catch (err: any) {
      setTestResultMsg({
        text: err.message || "Failed to dispatch test email",
        success: false,
      });
    } finally {
      setSendingTest(false);
    }
  };

  const filteredVillages = villages.filter((v) => {
    const matchesFilter = filter === "ALL" || v.alert_state === filter;
    const matchesSearch = v.name.toLowerCase().includes(search.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const getBadgeClass = (state: string) => {
    switch (state) {
      case "CRITICAL":
        return "badge-critical";
      case "WARNING":
        return "badge-high";
      case "WATCH":
        return "badge-moderate";
      case "RECOVERY":
        return "badge-recovery";
      default:
        return "badge-low";
    }
  };

  const getEmailStatusBadge = (status?: string) => {
    switch (status) {
      case "SENT":
        return (
          <span style={{ fontSize: "10px", padding: "2px 6px", borderRadius: "4px", backgroundColor: "rgba(16,185,129,0.2)", color: "#10b981", fontWeight: "700" }}>
            ✓ SENT
          </span>
        );
      case "SIMULATED":
        return (
          <span style={{ fontSize: "10px", padding: "2px 6px", borderRadius: "4px", backgroundColor: "rgba(56,189,248,0.2)", color: "#38bdf8", fontWeight: "700" }}>
            ℹ SIMULATED
          </span>
        );
      case "FAILED":
        return (
          <span style={{ fontSize: "10px", padding: "2px 6px", borderRadius: "4px", backgroundColor: "rgba(239,68,68,0.2)", color: "#ef4444", fontWeight: "700" }}>
            ✕ FAILED
          </span>
        );
      case "SUPPRESSED_COOLDOWN":
        return (
          <span style={{ fontSize: "10px", padding: "2px 6px", borderRadius: "4px", backgroundColor: "rgba(100,116,139,0.2)", color: "#94a3b8", fontWeight: "600" }}>
            ⏱ COOLDOWN
          </span>
        );
      default:
        return <span style={{ color: "#64748b", fontSize: "11px" }}>-</span>;
    }
  };

  return (
    <div
      style={{
        backgroundColor: "var(--bg-secondary)",
        border: "1px solid var(--border-color)",
        borderRadius: "8px",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
        boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
      }}
    >
      {/* Top Header & Tab Switcher */}
      <div
        style={{
          padding: "12px 16px",
          borderBottom: "1px solid var(--border-color)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "10px",
          backgroundColor: "#0d1527",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <ShieldAlert size={18} color="#ef4444" />
            <h4 style={{ fontSize: "14px", fontWeight: "800", letterSpacing: "-0.01em", margin: 0 }}>
              Emergency Alert & Response Center
            </h4>
          </div>

          {/* Tab Buttons */}
          <div style={{ display: "flex", gap: "2px", backgroundColor: "#1e293b", padding: "2px", borderRadius: "6px", border: "1px solid #334155" }}>
            <button
              onClick={() => setActiveTab("ACTIVE")}
              style={{
                padding: "4px 10px",
                fontSize: "11px",
                fontWeight: "700",
                borderRadius: "4px",
                border: "none",
                cursor: "pointer",
                backgroundColor: activeTab === "ACTIVE" ? "#2563eb" : "transparent",
                color: activeTab === "ACTIVE" ? "#ffffff" : "#94a3b8",
                display: "flex",
                alignItems: "center",
                gap: "5px",
              }}
            >
              <Activity size={12} />
              <span>Active Alerts ({villages.length})</span>
            </button>
            <button
              onClick={() => setActiveTab("HISTORY")}
              style={{
                padding: "4px 10px",
                fontSize: "11px",
                fontWeight: "700",
                borderRadius: "4px",
                border: "none",
                cursor: "pointer",
                backgroundColor: activeTab === "HISTORY" ? "#2563eb" : "transparent",
                color: activeTab === "HISTORY" ? "#ffffff" : "#94a3b8",
                display: "flex",
                alignItems: "center",
                gap: "5px",
              }}
            >
              <History size={12} />
              <span>Audit History ({historyItems.length})</span>
            </button>
            <button
              onClick={() => setActiveTab("EMAILS")}
              style={{
                padding: "4px 10px",
                fontSize: "11px",
                fontWeight: "700",
                borderRadius: "4px",
                border: "none",
                cursor: "pointer",
                backgroundColor: activeTab === "EMAILS" ? "#2563eb" : "transparent",
                color: activeTab === "EMAILS" ? "#ffffff" : "#94a3b8",
                display: "flex",
                alignItems: "center",
                gap: "5px",
              }}
            >
              <Mail size={12} />
              <span>Email Logs ({emailLogs.length})</span>
            </button>
          </div>
        </div>

        {/* Right Action Tools */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <button
            onClick={() => setShowTestModal(!showTestModal)}
            style={{
              padding: "4px 10px",
              fontSize: "11px",
              fontWeight: "700",
              borderRadius: "5px",
              border: "1px solid #38bdf8",
              backgroundColor: "rgba(56,189,248,0.12)",
              color: "#38bdf8",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "5px",
            }}
          >
            <Send size={12} />
            <span>Test Alert Email</span>
          </button>
          <button
            onClick={loadExtras}
            disabled={loadingExtras}
            style={{
              padding: "4px 8px",
              fontSize: "11px",
              borderRadius: "5px",
              border: "1px solid #334155",
              backgroundColor: "transparent",
              color: "#94a3b8",
              cursor: "pointer",
            }}
            title="Refresh logs"
          >
            <RefreshCw size={12} className={loadingExtras ? "animate-spin" : ""} />
          </button>
        </div>
      </div>

      {/* Test Email Dropdown Drawer */}
      {showTestModal && (
        <div
          style={{
            padding: "14px 18px",
            backgroundColor: "#0f172a",
            borderBottom: "1px solid #334155",
            display: "flex",
            flexDirection: "column",
            gap: "10px",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div style={{ fontSize: "12px", fontWeight: "700", color: "#f8fafc" }}>
              📧 Trigger Test Early Warning Email Dispatch
            </div>
            <button
              onClick={() => setShowTestModal(false)}
              style={{ background: "transparent", border: "none", color: "#64748b", cursor: "pointer" }}
            >
              <X size={14} />
            </button>
          </div>
          <form onSubmit={handleSendTestEmail} style={{ display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap" }}>
            <input
              type="email"
              placeholder="Recipient Email (default from .env if empty)"
              value={testEmailInput}
              onChange={(e) => setTestEmailInput(e.target.value)}
              style={{
                backgroundColor: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "4px",
                padding: "6px 10px",
                fontSize: "12px",
                color: "#ffffff",
                minWidth: "260px",
                outline: "none",
              }}
            />
            <select
              value={testSeverity}
              onChange={(e) => setTestSeverity(e.target.value as AlertState)}
              style={{
                backgroundColor: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "4px",
                padding: "6px 10px",
                fontSize: "12px",
                color: "#ffffff",
                outline: "none",
              }}
            >
              <option value="WARNING">Severity: WARNING</option>
              <option value="CRITICAL">Severity: CRITICAL</option>
            </select>
            <input
              type="text"
              placeholder="Sector / Village Name"
              value={testVillageName}
              onChange={(e) => setTestVillageName(e.target.value)}
              style={{
                backgroundColor: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "4px",
                padding: "6px 10px",
                fontSize: "12px",
                color: "#ffffff",
                width: "180px",
                outline: "none",
              }}
            />
            <button
              type="submit"
              disabled={sendingTest}
              style={{
                backgroundColor: "#2563eb",
                border: "none",
                borderRadius: "4px",
                padding: "6px 14px",
                fontSize: "12px",
                fontWeight: "700",
                color: "#ffffff",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              {sendingTest ? <Loader2 size={13} className="animate-spin" /> : <Send size={13} />}
              <span>{sendingTest ? "Sending..." : "Dispatch Alert"}</span>
            </button>
          </form>
          {testResultMsg && (
            <div
              style={{
                fontSize: "12px",
                padding: "6px 10px",
                borderRadius: "4px",
                backgroundColor: testResultMsg.success ? "rgba(16,185,129,0.15)" : "rgba(239,68,68,0.15)",
                color: testResultMsg.success ? "#34d399" : "#f87171",
                border: testResultMsg.success ? "1px solid #059669" : "1px solid #dc2626",
              }}
            >
              {testResultMsg.text}
            </div>
          )}
        </div>
      )}

      {/* TAB 1: ACTIVE SETTLEMENT ALERTS */}
      {activeTab === "ACTIVE" && (
        <>
          {/* Sub-toolbar: Search & State Filters */}
          <div
            style={{
              padding: "8px 16px",
              borderBottom: "1px solid var(--border-color)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              flexWrap: "wrap",
              gap: "8px",
              backgroundColor: "rgba(15, 23, 42, 0.4)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "6px", backgroundColor: "var(--bg-primary)", padding: "4px 8px", borderRadius: "4px", border: "1px solid var(--border-color)" }}>
              <Search size={14} color="var(--text-muted)" />
              <input
                type="text"
                placeholder="Search settlement..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                style={{
                  backgroundColor: "transparent",
                  border: "none",
                  outline: "none",
                  color: "var(--text-primary)",
                  fontSize: "12px",
                  width: "150px",
                }}
              />
            </div>

            <div style={{ display: "flex", gap: "4px", flexWrap: "wrap" }}>
              {["ALL", "CRITICAL", "WARNING", "WATCH", "RECOVERY", "NORMAL"].map((t) => (
                <button
                  key={t}
                  onClick={() => setFilter(t)}
                  style={{
                    padding: "3px 8px",
                    fontSize: "10px",
                    fontWeight: "700",
                    borderRadius: "4px",
                    border: filter === t ? "1px solid var(--accent-blue)" : "1px solid var(--border-color)",
                    backgroundColor: filter === t ? "rgba(37, 99, 235, 0.15)" : "transparent",
                    color: filter === t ? "var(--accent-blue)" : "var(--text-secondary)",
                    cursor: "pointer",
                  }}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "12px" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border-color)", color: "var(--text-muted)", backgroundColor: "var(--bg-primary)" }}>
                  <th style={{ padding: "10px 14px", fontWeight: "600" }}>Settlement</th>
                  <th style={{ padding: "10px 14px", fontWeight: "600" }}>Alert State</th>
                  <th style={{ padding: "10px 14px", fontWeight: "600" }}>Landslide Risk</th>
                  <th style={{ padding: "10px 14px", fontWeight: "600" }}>Flood Risk</th>
                  <th style={{ padding: "10px 14px", fontWeight: "600" }}>Dominant Factor</th>
                  <th style={{ padding: "10px 14px", fontWeight: "600" }}>Email Status</th>
                  <th style={{ padding: "10px 14px", fontWeight: "600" }}>Action Protocol</th>
                </tr>
              </thead>
              <tbody>
                {filteredVillages.map((v) => {
                  const isSelected = selectedVillageId === v.village_id;
                  const matchingAlert = alerts.find((a) => a.location_name === v.name);
                  return (
                    <tr
                      key={v.village_id}
                      onClick={() => onSelectVillage(v)}
                      style={{
                        borderBottom: "1px solid rgba(51, 65, 85, 0.4)",
                        backgroundColor: isSelected ? "rgba(37, 99, 235, 0.12)" : "transparent",
                        cursor: "pointer",
                        transition: "background 0.15s",
                      }}
                      onMouseEnter={(e) => {
                        if (!isSelected) e.currentTarget.style.backgroundColor = "rgba(30, 41, 59, 0.4)";
                      }}
                      onMouseLeave={(e) => {
                        if (!isSelected) e.currentTarget.style.backgroundColor = "transparent";
                      }}
                    >
                      <td style={{ padding: "10px 14px", fontWeight: "700", color: isSelected ? "var(--accent-blue)" : "var(--text-primary)" }}>
                        {v.name}
                      </td>
                      <td style={{ padding: "10px 14px" }}>
                        <span className={`badge ${getBadgeClass(v.alert_state)}`}>
                          {v.alert_state}
                        </span>
                      </td>
                      <td style={{ padding: "10px 14px", fontFamily: "monospace" }}>
                        <span style={{ fontWeight: "700", color: v.max_landslide_risk >= 0.6 ? "#f43f5e" : "#e2e8f0" }}>
                          {v.max_landslide_risk.toFixed(2)}
                        </span>
                      </td>
                      <td style={{ padding: "10px 14px", fontFamily: "monospace" }}>
                        <span>{v.max_flash_flood_risk.toFixed(2)}</span>
                      </td>
                      <td style={{ padding: "10px 14px", color: "var(--text-secondary)" }}>
                        {v.dominant_factor}
                      </td>
                      <td style={{ padding: "10px 14px" }}>
                        {getEmailStatusBadge(matchingAlert?.email_status)}
                      </td>
                      <td style={{ padding: "10px 14px", color: "var(--text-muted)", fontSize: "11px", maxWidth: "340px", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }} title={v.recommended_action}>
                        {v.recommended_action}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* TAB 2: AUDIT TRANSITION HISTORY */}
      {activeTab === "HISTORY" && (
        <div style={{ overflowX: "auto", maxHeight: "380px" }}>
          {historyItems.length === 0 ? (
            <div style={{ padding: "30px", textAlign: "center", color: "var(--text-muted)", fontSize: "12px" }}>
              No state transitions recorded yet. Changes in rainfall or slope stability trigger audit entries.
            </div>
          ) : (
            <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "12px" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border-color)", color: "var(--text-muted)", backgroundColor: "var(--bg-primary)" }}>
                  <th style={{ padding: "10px 14px", fontWeight: "600" }}>Timestamp</th>
                  <th style={{ padding: "10px 14px", fontWeight: "600" }}>Settlement</th>
                  <th style={{ padding: "10px 14px", fontWeight: "600" }}>Transition</th>
                  <th style={{ padding: "10px 14px", fontWeight: "600" }}>Risk</th>
                  <th style={{ padding: "10px 14px", fontWeight: "600" }}>Trigger Reason</th>
                  <th style={{ padding: "10px 14px", fontWeight: "600" }}>Email Status</th>
                </tr>
              </thead>
              <tbody>
                {historyItems.map((item) => (
                  <tr key={item.transition_id} style={{ borderBottom: "1px solid rgba(51, 65, 85, 0.4)" }}>
                    <td style={{ padding: "10px 14px", color: "var(--text-muted)", fontFamily: "monospace", fontSize: "11px" }}>
                      {new Date(item.timestamp).toLocaleTimeString()}
                    </td>
                    <td style={{ padding: "10px 14px", fontWeight: "700" }}>{item.location_name}</td>
                    <td style={{ padding: "10px 14px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "5px" }}>
                        <span className={`badge ${getBadgeClass(item.from_state)}`}>{item.from_state}</span>
                        <ChevronRight size={12} color="#64748b" />
                        <span className={`badge ${getBadgeClass(item.to_state)}`}>{item.to_state}</span>
                      </div>
                    </td>
                    <td style={{ padding: "10px 14px", fontFamily: "monospace", fontWeight: "700" }}>
                      {item.risk_score.toFixed(2)}
                    </td>
                    <td style={{ padding: "10px 14px", color: "var(--text-secondary)", fontSize: "11px" }}>
                      {item.trigger_reason}
                    </td>
                    <td style={{ padding: "10px 14px" }}>
                      {getEmailStatusBadge(item.email_status)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* TAB 3: EMAIL DISPATCH LOGS */}
      {activeTab === "EMAILS" && (
        <div style={{ overflowX: "auto", maxHeight: "380px" }}>
          {emailLogs.length === 0 ? (
            <div style={{ padding: "30px", textAlign: "center", color: "var(--text-muted)", fontSize: "12px" }}>
              No emergency alert emails dispatched yet. Click <strong>"Test Alert Email"</strong> above to dispatch one.
            </div>
          ) : (
            <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "12px" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border-color)", color: "var(--text-muted)", backgroundColor: "var(--bg-primary)" }}>
                  <th style={{ padding: "10px 14px", fontWeight: "600" }}>Timestamp</th>
                  <th style={{ padding: "10px 14px", fontWeight: "600" }}>Severity</th>
                  <th style={{ padding: "10px 14px", fontWeight: "600" }}>Recipient</th>
                  <th style={{ padding: "10px 14px", fontWeight: "600" }}>Subject</th>
                  <th style={{ padding: "10px 14px", fontWeight: "600" }}>Status</th>
                  <th style={{ padding: "10px 14px", fontWeight: "600" }}>Details</th>
                </tr>
              </thead>
              <tbody>
                {emailLogs.map((log) => (
                  <tr key={log.dispatch_id} style={{ borderBottom: "1px solid rgba(51, 65, 85, 0.4)" }}>
                    <td style={{ padding: "10px 14px", color: "var(--text-muted)", fontFamily: "monospace", fontSize: "11px" }}>
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </td>
                    <td style={{ padding: "10px 14px" }}>
                      <span className={`badge ${getBadgeClass(log.severity)}`}>{log.severity}</span>
                    </td>
                    <td style={{ padding: "10px 14px", fontFamily: "monospace", fontSize: "11px" }}>{log.recipient}</td>
                    <td style={{ padding: "10px 14px", color: "#f8fafc", fontSize: "11px", maxWidth: "260px", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {log.subject}
                    </td>
                    <td style={{ padding: "10px 14px" }}>
                      {getEmailStatusBadge(log.status)}
                    </td>
                    <td style={{ padding: "10px 14px", color: "var(--text-muted)", fontSize: "11px" }}>
                      {log.error_message || (log.simulated ? "Simulated test fixture" : "Delivered via SMTP")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
};
