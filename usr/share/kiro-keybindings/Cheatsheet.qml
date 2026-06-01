import QtCore
import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts

Window {
    id: win
    visible: true
    width: 1440
    height: 820
    flags: Qt.FramelessWindowHint | Qt.Dialog
    color: win.t.bgBottom

    // ── Themes ──────────────────────────────────────────────────────────
    readonly property var themes: ({
        "kiro": {
            bgTop: "#111C33", bgBottom: "#020617", cardBg: "#09ffffff", cardBorder: "#12ffffff",
            title: "#ffffff", subtext: "#94A3B8", desc: "#E2E8F0", plus: "#64748B",
            accents: ["#0195F7", "#2FC328", "#F59E0B", "#A855F7", "#22D3EE", "#F472B6"],
            keyPalette: { "super": "#0195F7", "ctrl": "#2FC328", "shift": "#F59E0B", "alt": "#A855F7", "key": "#94A3B8" },
            accentA: "#0195F7", accentB: "#2FC328", font: ""
        },
        "arcdark": {
            bgTop: "#404552", bgBottom: "#2F343F", cardBg: "#3B3F4C", cardBorder: "#2B2E39",
            title: "#D3DAE3", subtext: "#8B9BB4", desc: "#CFD6E6", plus: "#677691",
            accents: ["#5294E2", "#7FB0EA", "#5294E2", "#7FB0EA", "#5294E2", "#7FB0EA"],
            keyPalette: { "super": "#5294E2", "ctrl": "#66BB6A", "shift": "#E0A44B", "alt": "#B48EAD", "key": "#8B9BB4" },
            accentA: "#5294E2", accentB: "#7FB0EA", font: ""
        },
        "nord": {
            bgTop: "#3B4252", bgBottom: "#2E3440", cardBg: "#39404E", cardBorder: "#4C566A",
            title: "#ECEFF4", subtext: "#81A1C1", desc: "#D8DEE9", plus: "#4C566A",
            accents: ["#88C0D0", "#A3BE8C", "#EBCB8B", "#B48EAD", "#8FBCBB", "#81A1C1"],
            keyPalette: { "super": "#88C0D0", "ctrl": "#A3BE8C", "shift": "#EBCB8B", "alt": "#B48EAD", "key": "#81A1C1" },
            accentA: "#88C0D0", accentB: "#5E81AC", font: ""
        },
        "dracula": {
            bgTop: "#343746", bgBottom: "#282A36", cardBg: "#2E303E", cardBorder: "#44475A",
            title: "#F8F8F2", subtext: "#6272A4", desc: "#E6E6E6", plus: "#6272A4",
            accents: ["#BD93F9", "#50FA7B", "#FFB86C", "#FF79C6", "#8BE9FD", "#F1FA8C"],
            keyPalette: { "super": "#BD93F9", "ctrl": "#50FA7B", "shift": "#FFB86C", "alt": "#FF79C6", "key": "#6272A4" },
            accentA: "#BD93F9", accentB: "#FF79C6", font: ""
        },
        "gruvbox": {
            bgTop: "#3C3836", bgBottom: "#282828", cardBg: "#32302F", cardBorder: "#504945",
            title: "#EBDBB2", subtext: "#A89984", desc: "#EBDBB2", plus: "#928374",
            accents: ["#FABD2F", "#B8BB26", "#FE8019", "#D3869B", "#8EC07C", "#83A598"],
            keyPalette: { "super": "#83A598", "ctrl": "#B8BB26", "shift": "#FABD2F", "alt": "#D3869B", "key": "#A89984" },
            accentA: "#FABD2F", accentB: "#FE8019", font: ""
        },
        "catppuccin": {
            bgTop: "#1E1E2E", bgBottom: "#181825", cardBg: "#28283B", cardBorder: "#45475A",
            title: "#CDD6F4", subtext: "#A6ADC8", desc: "#CDD6F4", plus: "#6C7086",
            accents: ["#89B4FA", "#A6E3A1", "#F9E2AF", "#CBA6F7", "#94E2D5", "#F5C2E7"],
            keyPalette: { "super": "#89B4FA", "ctrl": "#A6E3A1", "shift": "#F9E2AF", "alt": "#CBA6F7", "key": "#A6ADC8" },
            accentA: "#89B4FA", accentB: "#CBA6F7", font: ""
        },
        "neon": {
            bgTop: "#0A0A14", bgBottom: "#050507", cardBg: "#260B1024", cardBorder: "#4022D3EE",
            title: "#EAFEFF", subtext: "#67E8F9", desc: "#C7F7FF", plus: "#3FB6C9",
            accents: ["#22D3EE", "#FF2BD6", "#B4FF39", "#A855F7", "#FF8A00", "#39FF14"],
            keyPalette: { "super": "#2D7CFF", "ctrl": "#39FF14", "shift": "#FFB800", "alt": "#FF2BD6", "key": "#5EEAD4" },
            accentA: "#22D3EE", accentB: "#FF2BD6", font: "monospace"
        }
    })
    // order shown in the switcher (label + swatch color)
    readonly property var themeList: [
        { key: "kiro", label: "Kiro", color: "#0195F7" },
        { key: "arcdark", label: "Arc-Dark", color: "#5294E2" },
        { key: "nord", label: "Nord", color: "#88C0D0" },
        { key: "dracula", label: "Dracula", color: "#BD93F9" },
        { key: "gruvbox", label: "Gruvbox", color: "#FABD2F" },
        { key: "catppuccin", label: "Catppuccin", color: "#89B4FA" },
        { key: "neon", label: "Neon", color: "#22D3EE" }
    ]

    // CLI override (used by --shot / --theme); blank → use the saved choice
    readonly property string cliTheme: (typeof appTheme !== "undefined" && appTheme) ? appTheme : ""
    property string themeName: cliTheme !== "" ? cliTheme : appSettings.theme
    readonly property var t: themes[themeName] !== undefined ? themes[themeName] : themes["kiro"]

    readonly property string headerStyle: (typeof appHeader !== "undefined" && appHeader) ? appHeader : "rule"
    readonly property string keyStyle: (typeof appKeys !== "undefined" && appKeys) ? appKeys : "mono"

    Settings {
        id: appSettings
        category: "ui"
        property string theme: "kiro"
    }

    property int total: {
        var n = 0
        var s = backend.sections
        for (var i = 0; i < s.length; i++)
            n += s[i].bindings.length
        return n
    }

    Component.onCompleted: {
        x = Math.round(Screen.width / 2 - width / 2)
        y = Math.round(Screen.height / 2 - height / 2)
        searchField.forceActiveFocus()
    }

    Rectangle {
        id: card
        anchors.fill: parent
        radius: 0
        gradient: Gradient {
            GradientStop { position: 0.0; color: win.t.bgTop }
            GradientStop { position: 1.0; color: win.t.bgBottom }
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 32
            spacing: 18

            // ── Header ──────────────────────────────────────────────────
            RowLayout {
                Layout.fillWidth: true
                spacing: 16

                Image {
                    source: logoPath
                    sourceSize.height: 46
                    fillMode: Image.PreserveAspectFit
                }

                ColumnLayout {
                    spacing: 1
                    Text {
                        text: "Keybindings"
                        color: win.t.title
                        font.pixelSize: 27
                        font.bold: true
                        font.family: win.t.font !== "" ? win.t.font : font.family
                    }
                    Text {
                        text: backend.wm + "  ·  " + win.total + " shortcuts"
                        color: win.t.subtext
                        font.pixelSize: 13
                        font.family: win.t.font !== "" ? win.t.font : font.family
                    }
                }

                Item { Layout.fillWidth: true }

                // theme switcher (hidden when a CLI theme is forced, e.g. --shot)
                Row {
                    spacing: 9
                    visible: win.cliTheme === ""
                    Repeater {
                        model: win.themeList
                        delegate: Rectangle {
                            width: 22
                            height: 22
                            radius: 11
                            color: modelData.color
                            border.width: win.themeName === modelData.key ? 2 : 0
                            border.color: "#ffffff"
                            scale: win.themeName === modelData.key ? 1.0 : 0.82
                            opacity: win.themeName === modelData.key ? 1.0 : 0.7
                            Behavior on scale { NumberAnimation { duration: 120 } }
                            Behavior on opacity { NumberAnimation { duration: 120 } }

                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: appSettings.theme = modelData.key
                                ToolTip.visible: containsMouse
                                ToolTip.text: modelData.label
                            }
                        }
                    }
                }

                Rectangle {
                    Layout.preferredWidth: 300
                    Layout.preferredHeight: 46
                    radius: 23
                    color: Qt.rgba(1, 1, 1, 0.06)
                    border.width: 1
                    border.color: searchField.activeFocus ? win.t.accentA : win.t.cardBorder

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 18
                        anchors.rightMargin: 18
                        spacing: 10
                        Text { text: "⌕"; color: win.t.subtext; font.pixelSize: 20 }
                        TextField {
                            id: searchField
                            Layout.fillWidth: true
                            placeholderText: "Type to filter…"
                            color: win.t.title
                            placeholderTextColor: win.t.subtext
                            background: null
                            font.pixelSize: 15
                            font.family: win.t.font !== "" ? win.t.font : font.family
                            onTextChanged: backend.setFilter(text)
                        }
                    }
                }
            }

            // ── Accent line ─────────────────────────────────────────────
            Rectangle {
                Layout.fillWidth: true
                height: 2
                gradient: Gradient {
                    orientation: Gradient.Horizontal
                    GradientStop { position: 0.0; color: win.t.accentA }
                    GradientStop { position: 1.0; color: win.t.accentB }
                }
            }

            // ── Body: 3 columns ─────────────────────────────────────────
            ScrollView {
                id: sv
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

                Flow {
                    width: sv.availableWidth
                    spacing: 22

                    Repeater {
                        model: backend.sections
                        delegate: Rectangle {
                            id: cardSection
                            property color accent: win.t.accents[index % win.t.accents.length]
                            width: Math.floor((sv.availableWidth - 2 * 22) / 3)
                            height: secCol.implicitHeight + 36
                            radius: 18
                            color: win.t.cardBg
                            border.width: 1
                            border.color: win.t.cardBorder

                            Rectangle {
                                anchors { left: parent.left; right: parent.right; top: parent.top; leftMargin: 18; rightMargin: 18 }
                                height: 3
                                radius: 2
                                color: cardSection.accent
                                opacity: 0.85
                            }

                            ColumnLayout {
                                id: secCol
                                x: 20
                                y: 20
                                width: parent.width - 40
                                spacing: 6

                                // category header — style chosen by win.headerStyle
                                Item {
                                    id: hdrItem
                                    Layout.fillWidth: true
                                    implicitHeight: 22
                                    property string label: modelData.name.toUpperCase()

                                    RowLayout {
                                        visible: win.headerStyle === "rule"
                                        anchors.fill: parent
                                        spacing: 12
                                        Text {
                                            text: hdrItem.label
                                            color: cardSection.accent
                                            font.pixelSize: 12
                                            font.bold: true
                                            font.letterSpacing: 1.4
                                            font.family: win.t.font !== "" ? win.t.font : font.family
                                        }
                                        Rectangle {
                                            Layout.fillWidth: true
                                            height: 1
                                            color: Qt.rgba(cardSection.accent.r, cardSection.accent.g, cardSection.accent.b, 0.35)
                                        }
                                    }

                                    RowLayout {
                                        visible: win.headerStyle === "bar"
                                        anchors.fill: parent
                                        spacing: 10
                                        Rectangle { width: 3; height: 15; radius: 1.5; color: cardSection.accent }
                                        Text {
                                            text: hdrItem.label
                                            color: win.t.title
                                            font.pixelSize: 12
                                            font.bold: true
                                            font.letterSpacing: 1.2
                                            font.family: win.t.font !== "" ? win.t.font : font.family
                                        }
                                    }

                                    RowLayout {
                                        visible: win.headerStyle === "dot"
                                        anchors.fill: parent
                                        spacing: 9
                                        Rectangle { width: 8; height: 8; radius: 4; color: cardSection.accent; Layout.alignment: Qt.AlignVCenter }
                                        Text {
                                            text: hdrItem.label
                                            color: win.t.title
                                            font.pixelSize: 12
                                            font.bold: true
                                            font.letterSpacing: 1.2
                                            font.family: win.t.font !== "" ? win.t.font : font.family
                                        }
                                    }

                                    Text {
                                        visible: win.headerStyle === "plain"
                                        anchors.verticalCenter: parent.verticalCenter
                                        text: hdrItem.label
                                        color: win.t.subtext
                                        font.pixelSize: 12
                                        font.bold: true
                                        font.letterSpacing: 2.2
                                        font.family: win.t.font !== "" ? win.t.font : font.family
                                    }
                                }

                                Item { height: 4 }

                                Repeater {
                                    model: modelData.bindings
                                    delegate: BindingRow {
                                        Layout.fillWidth: true
                                        desc: modelData.desc
                                        tokens: modelData.tokens
                                        descColor: win.t.desc
                                        keyPalette: win.t.keyPalette
                                        capFont: win.t.font
                                        capStyle: win.keyStyle
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // ── Footer ──────────────────────────────────────────────────
            RowLayout {
                Layout.fillWidth: true
                Text {
                    text: "type to filter  ·  Esc to close"
                    color: win.t.subtext
                    font.pixelSize: 12
                    font.family: win.t.font !== "" ? win.t.font : font.family
                }
                Item { Layout.fillWidth: true }
                Text {
                    text: "◆ same key on every Kiro desktop"
                    color: win.t.subtext
                    font.pixelSize: 12
                    font.family: win.t.font !== "" ? win.t.font : font.family
                }
            }
        }
    }

    Shortcut {
        sequence: "Escape"
        onActivated: Qt.quit()
    }
}
