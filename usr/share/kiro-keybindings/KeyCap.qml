import QtQuick

// One key token. capStyle controls how "button-like" it looks:
//   boxed   — filled gradient chip (button look)
//   outline — thin border, no fill
//   text    — pure typography, modifiers colored, no box
//   mono    — pure typography in a monospace face
Item {
    property string label: ""
    property string kind: "key"
    property var keyColors: ({})
    property string capFont: ""
    property string capStyle: "boxed"

    readonly property color base: keyColors[kind] !== undefined
        ? keyColors[kind]
        : (keyColors["key"] !== undefined ? keyColors["key"] : "#64748B")
    readonly property bool isMod: kind !== "key"
    readonly property bool plain: capStyle === "text" || capStyle === "mono"

    implicitWidth: plain ? txt.implicitWidth + 2 : Math.max(30, txt.implicitWidth + 22)
    implicitHeight: 30

    // filled chip
    Rectangle {
        anchors.fill: parent
        visible: capStyle === "boxed"
        radius: 8
        gradient: Gradient {
            GradientStop { position: 0.0; color: Qt.rgba(base.r, base.g, base.b, 0.34) }
            GradientStop { position: 1.0; color: Qt.rgba(base.r, base.g, base.b, 0.13) }
        }
        border.width: 1
        border.color: Qt.rgba(base.r, base.g, base.b, 0.62)
        Rectangle {
            anchors { left: parent.left; right: parent.right; top: parent.top; margins: 3 }
            height: 2
            radius: 2
            color: Qt.rgba(1, 1, 1, 0.16)
        }
    }

    // outline only
    Rectangle {
        anchors.fill: parent
        visible: capStyle === "outline"
        radius: 8
        color: "transparent"
        border.width: 1
        border.color: Qt.rgba(base.r, base.g, base.b, 0.55)
    }

    Text {
        id: txt
        anchors.centerIn: parent
        text: label
        color: plain ? base : "white"
        font.pixelSize: 13
        font.bold: true
        font.family: capStyle === "mono"
            ? "monospace"
            : (capFont !== "" ? capFont : Qt.application.font.family)
    }
}
