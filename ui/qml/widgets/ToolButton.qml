import QtQuick 2.0
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtGraphicalEffects 1.0

Button {
    id: btn
    property color textColor: "#ddd"

    style: ButtonStyle {
        background: Rectangle {
            id : btnRect
            border.width: control.activeFocus ? 2 : 1
            border.color: control.pressed || control.checked ? "#353535" : "#252525"
            radius: 4
            gradient: Gradient {
                GradientStop {
                    position: 0
                    color: control.pressed || control.checked ? "#151515" : "#454343"
                }
                GradientStop {
                    position: 1
                    color: control.pressed || control.checked ? "#353535" : "#252525"
                }
            }
        }

        label: Item {
            implicitWidth: row.implicitWidth
            implicitHeight: row.implicitHeight
            Row {
                id: row
                anchors.centerIn: parent
                spacing: 2
                Image {
                    source: control.iconSource
                    anchors.verticalCenter: parent.verticalCenter
                }
                Text {
                    id: text
                    anchors.verticalCenter: parent.verticalCenter
                    text: control.text
                    font.pointSize: 8
                    color: control.textColor
                }
            }
        }
    }
}
