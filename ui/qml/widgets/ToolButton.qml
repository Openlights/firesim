import QtQuick 2.0
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4

Button {
    style: ButtonStyle {
        background: Rectangle {
            border.width: control.activeFocus ? 2 : 1
            border.color: "#333"
            radius: 4
            gradient: Gradient {
                GradientStop {
                    position: 0
                    color: control.pressed || control.checked ? "#111" : "#222"
                }
                GradientStop {
                    position: 1
                    color: control.pressed || control.checked ? "#222" : "#333"
                }
            }
        }
    }
}
