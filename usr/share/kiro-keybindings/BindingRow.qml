import QtQuick
import QtQuick.Layouts

// One keybinding: color-coded keycaps joined by "+", then the description.
// Highlights on hover. Colors/font come from the theme via properties.
Item {
    id: row
    property string desc: ""
    property var tokens: []
    property color descColor: "#E2E8F0"
    property var keyPalette: ({})
    property string capFont: ""
    property string capStyle: "boxed"
    implicitHeight: 40

    Rectangle {
        anchors.fill: parent
        anchors.leftMargin: -10
        anchors.rightMargin: -10
        radius: 9
        color: Qt.rgba(1, 1, 1, 0.06)
        opacity: hover.hovered ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: 120 } }
    }
    HoverHandler { id: hover }

    RowLayout {
        anchors.fill: parent
        spacing: 12

        Row {
            spacing: 5
            Repeater {
                model: tokens
                delegate: Row {
                    spacing: 5
                    Text {
                        visible: index > 0
                        text: "+"
                        color: "#64748B"
                        font.pixelSize: 12
                        font.bold: true
                        anchors.verticalCenter: parent.verticalCenter
                    }
                    KeyCap {
                        label: modelData.label
                        kind: modelData.kind
                        keyColors: row.keyPalette
                        capFont: row.capFont
                        capStyle: row.capStyle
                    }
                }
            }
        }

        Text {
            Layout.fillWidth: true
            text: desc
            color: descColor
            font.pixelSize: 13
            font.family: capFont !== "" ? capFont : Qt.application.font.family
            elide: Text.ElideRight
            verticalAlignment: Text.AlignVCenter
        }
    }
}
