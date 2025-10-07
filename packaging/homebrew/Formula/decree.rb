class Decree < Formula
  include Language::Python::Virtualenv
  desc "Python reimplementation of adr-tools"
  homepage "https://github.com/steven-cutting/decree"
  url "https://files.pythonhosted.org/packages/source/d/decree/decree-0.1.0.tar.gz"
  sha256 "<REPLACE_WITH_SDIST_SHA256>"
  license "BSD-3-Clause"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "Usage:", shell_output("#{bin}/decree --help")
  end
end
